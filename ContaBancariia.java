public class ContaBancariia {
    private int numConta;
    protected String tipo;
    private String dono;
    private float saldo;
    private boolean status;


//Metodos especiais

public void abrirConta(String t){
    this.settipo(t);
    this.setstatus(true);
    if (t == "CC"){
        this.setsaldo(50);
    }else if (t == "CP"){
        this.setsaldo(150);
    }
}
public void fecharConta(){ 
    if (this.getsaldo() > 0){
        System.out.println("Conta com dinheiro, não posso fechar");
     } else if (this.getsaldo() < 0){
            System.out.println("Conta em débito, não posso fechar");
     } else {
                this.setstatus(false);
            System.out.println("Conta fechada com sucesso");
}
}
public void depositar(float v){ 
    if (this.getstatus()) {
        this.setsaldo(this.getsaldo() + v);
        System.out.println("Depósito realizado na conta de " + this.getdono());
         } else {
            System.out.println("Impossível depositar em uma conta fechada");
         }
        }


public void sacar(float v){
     if (this.getstatus()) {
        if (this.getsaldo() >= v) {  //aqui estou puxando o saldo dele é verificando se o saldo é igual ou maior o que ele quer sacar
            this.setsaldo(this.getsaldo() - v); // aqui se ele conseguir sacar estou subtraindo o valor do saque do saldo atual
            System.out.println("Saque realizado na conta de " + this.getdono());
        } else { //agr se ele não tiver salvo suficiente para sacar o valor que ele quer, ele vai mostrar a mensagem de saldo insuficiente
            System.out.println("Saldo insuficiente para saque");
        }
    } else { //e se o status da conta for falso, ou seja, a conta estiver fechada, ele vai mostrar a mensagem abaixo
        System.out.println("Impossível sacar de uma conta fechada");
    }

}
public void pagarMensal(){ 
        int v = 0;
    if (this.gettipo() == "CC") {
        v = 12;
    } else if (this.gettipo() == "CP") {
        v = 20;
    }
    if (this.getstatus()) {
        this.setsaldo(this.getsaldo() - v); 
    System.out.println("Mensalidade paga com sucesso por " + this.getdono());
        } else {
            System.out.println("Impossível pagar uma conta fechada");
        }
    }




//Setters e Getters
public void setnumConta(int n){
    this.numConta = n;
}
public int getnumConta(){
    return this.getnumConta();
}
public void settipo(String t){
    this.tipo = t;

}
public String gettipo(){
    return this.tipo;
}
public void setdono(String d){
    this.dono = d;
}
public String getdono(){
    return this.dono;
}
public void setsaldo(float s){
    this.saldo = s;
}
public float getsaldo(){
    return this.saldo;
}
public void setstatus(boolean st){
    this.status = st;
}
public boolean getstatus(){
    return this.status;
}

}
