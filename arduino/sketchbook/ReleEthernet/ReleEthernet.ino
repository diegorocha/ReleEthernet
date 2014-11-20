#include <EtherCard.h>

// CONFIGURACOES GERAIS
#define QTD_RELES 1
#define ON 1
#define OFF 0
#define ON_STR "ON"
#define OFF_STR "OFF"

// CONFIGURACOES DE REDE
#define STATIC 0 // Caso queira definir um ip estático mude de 0 para 1 
#if STATIC
static byte myip[] = { 192,168,0,10 }; // Endereço IP estático a ser definido a interface Ethernet
static byte gwip[] = { 192,168,0,1 }; // Endereço IP do Gateway da sua rede
#endif
static byte mymac[] = { 0x74,0x69,0x69,0x2D,0x30,0x21 }; // MAC Address da interface ethernet - deve ser único na sua rede local
byte Ethernet::buffer[500];
BufferFiller bfill;

// CONFIGURACOES DO RELE
int rele[] = {5};
int estadoRele[] = {0};

// FUNCAO QUE PROCESSA A REQUISICAO
word processRequest(int n_rele, char job){
    int alterado = 0;
    char output[4];
    bfill = ether.tcpOffset();
    
    // REQUISICAO INVALIDA
    if (n_rele < 0 || n_rele >= QTD_RELES) {
      bfill.emit_p(PSTR("HTTP/1.0 200 OK\r\n"
        "Content-Type: text/html\r\n"
        "\r\n"
        "ERROR\r\n"));
      return bfill.position();
    }
    
    // TRATA A REQUISICAO
    if (job == '0') {
      estadoRele[n_rele] = OFF;
      alterado = 1;
    }
    if (job == '1') {
      estadoRele[n_rele] = ON;
      alterado = 1;
    }
    if (job == '!') {
      estadoRele[n_rele] = (estadoRele[n_rele] == OFF ? ON : OFF); // INVERTE  O SINAL
      alterado = 1;
    }
    // '?' NAO E TRATADO POIS O ESTADO ATUAL DO RELE SEMPRE E EXIBIDO AO FINAL DO PROCESSAMENTO
    
    // ALTERA O SINAL DIGITAL DO RELE SE NECESSARIO
    if (alterado == 1) {
      digitalWrite(rele[n_rele], (estadoRele[n_rele] == OFF ? LOW : HIGH));
    }
    
    // EXIBE O VALOR ATUAL DO RELE
    strcpy(output, (estadoRele[n_rele] == ON ? ON_STR : OFF_STR));
    
    //GERA A RESPOSTA DA REQUISICAO
    bfill.emit_p(PSTR( 
      "HTTP/1.0 200 OK\r\n"
      "Content-Type: text/html\r\n"
      "\r\n"
      "RELE $D: $S\r\n"
      ), n_rele, output);
    return bfill.position();
}

void setup(){
   // INICIALIZA PORTA SERIAL
   Serial.begin(57600);
   
   // INICIALIZA PORTAS UTILIZADAS PELOS RELES
   for(int i = 0; i<QTD_RELES; i++){
     pinMode(rele[i], OUTPUT);
     digitalWrite(rele[i], LOW);
   }
   
   // CARREGA BIBLIOTECA DA SHIELD ETHERNET E OBTEM IP
   Serial.println("\n[Iniciando Servidor]");
   if (ether.begin(sizeof Ethernet::buffer, mymac, 10) == 0)
      Serial.println("Falha ao acessar o controlador Ethernet.");
   #if STATIC
      ether.staticSetup(myip, gwip);
   #else
      if (!ether.dhcpSetup())
         Serial.println("DHCP falhou!");
   #endif
   ether.printIp("IP: ", ether.myip);
   ether.printIp("GW: ", ether.gwip);
   ether.printIp("DNS: ", ether.dnsip);
}

void loop(){
  // TRATA UMA REQUISICAO SE HOUVER
  word len = ether.packetReceive();
  word pos = ether.packetLoop(len); 
  if (pos) {
      // AJUSTA OS PARAMETROS DA FUNCAO CONFORME A URL
      int rele = -1;
      char job = ' ';
      if(strstr((char *)Ethernet::buffer + pos, "GET /0?") != 0) {
        rele = 0;
        job = '?';       
      }
      if(strstr((char *)Ethernet::buffer + pos, "GET /0!") != 0) {
        rele = 0;
        job = '!';       
      }
      if(strstr((char *)Ethernet::buffer + pos, "GET /00") != 0) {
        rele = 0;
        job = '0';       
      }
      if(strstr((char *)Ethernet::buffer + pos, "GET /01") != 0) {
        rele = 0;
        job = '1';       
      }
      
      // CHAMA A FUNCAO COM OS PARAMETROS
      ether.httpServerReply(processRequest(rele, job));
   }
}
