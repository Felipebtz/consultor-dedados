"""
Gerenciador BigQuery: cria dataset/tabelas e insere dados da coleta Omie.
Substitui o fluxo MySQL quando GOOGLE_APPLICATION_CREDENTIALS + GCP_PROJECT_ID + BIGQUERY_DATASET estão configurados.
Suporta credenciais inline (GOOGLE_APPLICATION_CREDENTIALS_JSON) para Vercel/serverless.
"""
import os
import tempfile
import logging
import json
import re
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any, Optional

from google.cloud import bigquery
from google.cloud.bigquery import SchemaField

logger = logging.getLogger(__name__)

# Tamanho do lote para inserção (BigQuery recomenda até 500 por streaming insert)
INSERT_BATCH_SIZE = 500


def _mysql_type_to_bigquery(mysql_type: str) -> str:
    """Converte tipo MySQL (string) para tipo BigQuery."""
    t = mysql_type.upper().strip()
    # Remove sufixos comuns (PRIMARY KEY, AUTO_INCREMENT, UNIQUE, DEFAULT ...)
    t = re.sub(r"\s+PRIMARY\s+KEY.*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+AUTO_INCREMENT.*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+UNIQUE.*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+DEFAULT\s+.*", "", t, flags=re.IGNORECASE)
    t = t.strip()
    if t.startswith("BIGINT") or t.startswith("INT "):
        return "INTEGER"
    if t.startswith("INT(") or "INT" == t:
        return "INTEGER"
    if t.startswith("VARCHAR") or t.startswith("CHAR") or t.startswith("TEXT"):
        return "STRING"
    if t.startswith("DECIMAL") or t.startswith("NUMERIC"):
        return "NUMERIC"
    if t.startswith("FLOAT") or t.startswith("DOUBLE"):
        return "FLOAT64"
    if t == "DATE":
        return "DATE"
    if t.startswith("DATETIME"):
        return "DATETIME"
    if t.startswith("TIMESTAMP"):
        return "TIMESTAMP"
    if t.startswith("TINYINT"):
        return "INTEGER"
    return "STRING"


def _resolve_credentials_path(gcp_settings) -> Optional[str]:
    """
    Retorna o caminho do arquivo de credenciais para GOOGLE_APPLICATION_CREDENTIALS.
    Na Vercel o JSON vem em variável (GOOGLE_APPLICATION_CREDENTIALS_JSON ou valor inline);
    grava em arquivo temporário para a lib Google auth conseguir ler.
    Se o valor parecer JSON (começa com '{'), sempre grava em arquivo; não exige json.loads
    válido (evita "File ... was not found" quando o JSON colado tem formatação diferente).
    """
    json_content = getattr(gcp_settings, "GOOGLE_APPLICATION_CREDENTIALS_JSON", None) or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    path_value = getattr(gcp_settings, "GOOGLE_APPLICATION_CREDENTIALS", None) or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    def _write_json_to_temp(content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".json", prefix="gcp-credentials-")
        try:
            os.write(fd, content.encode("utf-8"))
        finally:
            os.close(fd)
        return path

    if json_content and isinstance(json_content, str) and json_content.strip().startswith("{"):
        return _write_json_to_temp(json_content)
    if path_value and isinstance(path_value, str) and path_value.strip().startswith("{"):
        return _write_json_to_temp(path_value)
    return path_value


class BigQueryManager:
    """
    Gerencia dataset e tabelas no BigQuery; insere dados em lote.
    Interface compatível com o uso no orquestrador (create_table, insert_batch).
    """

    def __init__(self, gcp_settings):
        from src.config import GcpSettings
        self.settings: GcpSettings = gcp_settings
        project = self.settings.project_id
        dataset_id = self.settings.dataset_id
        if not project or not dataset_id:
            raise ValueError(
                "BigQuery exige GCP_PROJECT_ID e BIGQUERY_DATASET no .env"
            )
        credentials_path = _resolve_credentials_path(self.settings)
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self._client = bigquery.Client(project=project)
        self._project = project
        self._dataset_id = dataset_id
        self._dataset_ref = f"{project}.{dataset_id}"

    def create_database_if_not_exists(self):
        """Cria o dataset no BigQuery se não existir (equivalente ao banco MySQL)."""
        try:
            dataset = bigquery.Dataset(self._dataset_ref)
            dataset.location = "US"
            self._client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Dataset BigQuery '{self._dataset_ref}' verificado/criado")
        except Exception as e:
            logger.error(f"Erro ao criar dataset BigQuery: {str(e)}")
            raise

    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """
        Cria tabela no BigQuery a partir do schema (coluna -> tipo MySQL).
        Converte tipos MySQL para BigQuery.
        """
        try:
            table_id = f"{self._dataset_ref}.{table_name}"
            existing = self._client.get_table(table_id)
            if existing:
                logger.info(f"Tabela BigQuery '{table_id}' já existe")
                return True
        except Exception:
            pass
        try:
            fields = []
            for col, type_def in schema.items():
                bq_type = _mysql_type_to_bigquery(type_def)
                fields.append(SchemaField(col, bq_type, mode="NULLABLE"))
            table = bigquery.Table(table_id, schema=fields)
            self._client.create_table(table, exists_ok=True)
            logger.info(f"Tabela BigQuery '{table_id}' criada/verificada")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabela BigQuery '{table_name}': {str(e)}")
            return False

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
        if not isinstance(d, dict):
            return d
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v, ensure_ascii=False) if v else None))
            else:
                items.append((new_key, v))
        return dict(items)

    def _normalize_date_string(self, s: str) -> Optional[str]:
        """Converte string de data DD/MM/YYYY ou DD-MM-YYYY para YYYY-MM-DD (BigQuery)."""
        if not s or not isinstance(s, str):
            return None
        s = s.strip()
        if not s:
            return None
        # Já está em YYYY-MM-DD
        if re.match(r"^\d{4}-\d{2}-\d{2}", s):
            return s[:10] if len(s) >= 10 else s
        # DD/MM/YYYY ou DD/MM/YYYY HH:MM:SS
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})(?:\s+(\d{1,2}):(\d{1,2}):(\d{1,2}))?$", s)
        if m:
            d, mo, y = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
            if m.group(4) is not None:
                return f"{y}-{mo}-{d} {m.group(4).zfill(2)}:{m.group(5).zfill(2)}:{m.group(6).zfill(2)}"
            return f"{y}-{mo}-{d}"
        # DD-MM-YYYY ou DD-MM-YYYY HH:MM:SS
        m = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})(?:\s+(\d{1,2}):(\d{1,2}):(\d{1,2}))?$", s)
        if m:
            d, mo, y = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
            if m.group(4) is not None:
                return f"{y}-{mo}-{d} {m.group(4).zfill(2)}:{m.group(5).zfill(2)}:{m.group(6).zfill(2)}"
            return f"{y}-{mo}-{d}"
        return None

    def _serialize_value(self, v: Any) -> Any:
        """Serializa valor para JSON compatível com BigQuery (datas, Decimal, etc.)."""
        if v is None:
            return None
        if isinstance(v, (dict, list)):
            return json.dumps(v, ensure_ascii=False)
        if isinstance(v, Decimal):
            return float(v)
        if isinstance(v, (datetime, date)):
            return v.strftime("%Y-%m-%d") if isinstance(v, date) and not isinstance(v, datetime) else v.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(v, "isoformat"):  # date/datetime de outros módulos
            return v.isoformat()[:19].replace("T", " ")
        # String que parece data DD/MM/YYYY ou DD-MM-YYYY (Omie)
        if isinstance(v, str):
            normalized = self._normalize_date_string(v)
            if normalized is not None:
                return normalized
        return v

    def _prepare_row(self, record: Dict[str, Any], columns: List[str]) -> Dict[str, Any]:
        flat = self._flatten_dict(record)
        row = {}
        for col in columns:
            v = flat.get(col)
            row[col] = self._serialize_value(v)
        return row

    def insert_batch(self, table_name: str, data: List[Dict[str, Any]]) -> int:
        """
        Insere dados na tabela BigQuery em lotes (streaming insert).
        Retorna o número de linhas inseridas (aproximado em caso de erros parciais).
        """
        if not data:
            return 0
        table_id = f"{self._dataset_ref}.{table_name}"
        try:
            table = self._client.get_table(table_id)
            columns = [f.name for f in table.schema]
        except Exception as e:
            logger.error(f"Erro ao obter schema da tabela '{table_name}': {str(e)}")
            return 0
        total = 0
        for i in range(0, len(data), INSERT_BATCH_SIZE):
            chunk = data[i : i + INSERT_BATCH_SIZE]
            rows = []
            id_col = next((c for c in columns if c.lower() == "id"), None)
            for record in chunk:
                row = self._prepare_row(record, columns)
                row = {k: v for k, v in row.items() if k in columns}
                if id_col is not None:
                    val = row.get(id_col)
                    if val is None or val == "":
                        row[id_col] = str(uuid.uuid4())
                rows.append(row)
            if not rows:
                continue
            try:
                errors = self._client.insert_rows_json(table_id, rows)
                if errors:
                    first = errors[0]
                    msg = first.get("errors", [{}])[0].get("message", str(first)) if isinstance(first, dict) else str(first)
                    logger.warning(
                        f"BigQuery '{table_name}': {len(errors)} erros em {len(rows)} linhas. "
                        f"Exemplo: {msg[:200]}"
                    )
                total += max(0, len(rows) - len(errors))
            except Exception as e:
                logger.error(f"Erro ao inserir em BigQuery '{table_name}': {e}")
        logger.info(f"Inseridos {total} registros na tabela BigQuery '{table_name}'")
        return total

    def truncate_table(self, table_name: str) -> bool:
        """Esvazia a tabela antes da carga (full refresh, evita duplicação)."""
        table_id = f"{self._dataset_ref}.{table_name}"
        try:
            self._client.query(f"TRUNCATE TABLE `{self._project}.{self._dataset_id}.{table_name}`").result()
            logger.info(f"Tabela BigQuery '{table_name}' truncada para nova carga")
            return True
        except Exception as e:
            logger.warning(f"Truncate em '{table_name}' falhou (tabela pode estar vazia ou não existir): {e}")
            return False

    def get_existing_keys(self, table_name: str, key_columns: List[str]) -> set:
        """Retorna o conjunto de chaves já presentes na tabela (para carga incremental)."""
        if not key_columns:
            return set()
        table_id = f"`{self._project}.{self._dataset_id}.{table_name}`"
        cols = ", ".join(key_columns)
        query = f"SELECT {cols} FROM {table_id}"
        try:
            rows = self.execute_query(query)
            if not rows:
                return set()
            if len(key_columns) == 1:
                k = key_columns[0]
                return {self._serialize_value(r.get(k)) for r in rows if r.get(k) is not None}
            return {tuple(self._serialize_value(r.get(c)) for c in key_columns) for r in rows}
        except Exception as e:
            logger.warning(f"Erro ao buscar chaves existentes em '{table_name}': {e}")
            return set()

    def get_key_from_record(self, record: Dict[str, Any], key_columns: List[str]) -> Any:
        """Extrai a chave do registro (mesmo flatten que o insert usa). Para comparar com get_existing_keys."""
        if not key_columns:
            return None
        flat = self._flatten_dict(record)
        vals = [self._serialize_value(flat.get(c)) for c in key_columns]
        if len(key_columns) == 1:
            return vals[0]
        return tuple(vals)

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Executa uma query SELECT no BigQuery e retorna lista de dicionários.
        Usado pelo dashboard para stats e listagem de tabelas.
        """
        try:
            job = self._client.query(query)
            rows = job.result()
            columns = [f.name for f in rows.schema]
            return [dict(zip(columns, row.values())) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao executar query BigQuery: {str(e)}")
            return []

    def get_table_count(self, table_name: str) -> int:
        """Retorna COUNT(*) da tabela (para o dashboard)."""
        table_id = f"{self._dataset_ref}.{table_name}"
        q = f"SELECT COUNT(*) as total FROM `{table_id}`"
        result = self.execute_query(q)
        return int(result[0]["total"]) if result else 0

    def table_ref(self, table_name: str) -> str:
        """Retorna referência qualificada para uso em queries: `project.dataset.table`."""
        return f"`{self._dataset_ref}.{table_name}`"

    def close_pool(self):
        """Compatível com orquestrador; BigQuery client não exige close."""
        pass
