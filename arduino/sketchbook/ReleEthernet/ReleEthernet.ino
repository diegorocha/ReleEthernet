#include <EtherCard.h>
#include <TM1638.h>

// PORTAS DIGITAIS USADAS: 5, 6, 7, 8
// 5: DIGITAL OUTPUT DO RELE
// 6: STROBE DO DISPLAY
// 7: CLOCK DO DISPLAY
// 8: DIGITAL I/O DO DISPLAY

// CONFIGURACOES GERAIS
#define QTD_RELES 1
#define ON 1
#define OFF 0
#define ON_STR "ON"
#define OFF_STR "OFF"

// CONFIGURACOES DE REDE
#define STATIC 1 // Caso queira definir um ip estático mude de 0 para 1 
#if STATIC
static byte myip[] = { 192, 168, 0, 10 }; // Endereço IP estático a ser definido a interface Ethernet
static byte gwip[] = { 192, 168, 0, 1 }; // Endereço IP do Gateway da sua rede
#endif
static byte mymac[] = { 0x74,0x69,0x69,0x2D,0x30,0x21 }; // MAC Address da interface ethernet - deve ser único na sua rede local
byte Ethernet::buffer[500];
BufferFiller bfill;

// CONFIGURACOES DO RELE
int rele[] = {5};
int estadoRele[] = {0};

// CONFIGURACOES DO DISPLAY
TM1638 module(8, 7, 6);
byte exibe_ip = 1;
String ip_str;
byte tam;
char ip[16];
byte ip_p;
int display_i = 0;
int qtd_loop = 0;
#define LOOP_FLAG 150

// CONFIGURACOES DE PORTA 13 ALWAYS ON
#define PORTA_13_ALWAYS_ON 1 //O: DESLIGADO; 1: LIGADO

// RESET FUNCTION
void(* resetFunc) (void) = 0;

void changeRelayState(int n_rele, char job){
  int alterado = 0;
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
    module.setLED((estadoRele[n_rele] == OFF ? TM1638_COLOR_NONE : TM1638_COLOR_GREEN), n_rele);
  }
}

// INICIALIZA AS VARIAVEIS GLOBAIS PARA ESCREVER O IP NO DISPLAY
void setupIpOnDisplay(){
  ip_str = String(ether.myip[0]) + "." + String(ether.myip[1]) + "." + String(ether.myip[2]) + "." + String(ether.myip[3]);
  tam = ip_str.length();
  ip_str.toCharArray(ip, 16); 
  ip_p = 0;
}

// ESCREVE NO DISPLAY O IP, CASO NAO CAIBA FAZ UMA ROTATORIA
void writeIpOnDisplay(){
  int display_p = display_i - 1; // Controla a posicao do display onde o endereco comeca a ser escrito
  byte i = 0;
  byte value = 0;
  
  // LIMPA TODAS AS POSICOES DO DISPLAY
  module.clearDisplay();
  
  // ESCREVE DA POSICAO INICIAL ATE O FIM DO DISPLAY OU FIM DA STRING
  for(i = ip_p; (display_p < 7 && i < tam); i++){
    if (ip[i] >= '0' && ip[i] <= '9')
    {
      display_p++; // Avanca para proxima posicao a ser escrita
      value = ip[i] - 48; // Obtem o valor ASCII do caractere numerico
      module.setDisplayDigit(value, display_p, false);
    }
    if (ip[i] == '.' && display_p > -1) // Ignora um ponto no inicio da String
    {
      module.setDisplayDigit(value, display_p, true); // Acende o ponto da posicao atual
    }
  }

  // SE NAO COUBER NO DISPLAY
  if(tam>= 12){
    if(display_i == 0){
      // A posicao inicial e a primeira, entao deve permanecer nessa posicao e a string deve continuar avancando
      ip_p++;
    }else{
      // Nao esta no inicio do display, entao a posicao inicial deve retrocedor e a string comecar do inicio
      display_i--;
      if(display_i < 0){
        display_i = 0;
      }
      ip_p = 0;  
    }
    
    // Se a String acabou faz a string recomecar na ultima posicao do display
    if(ip_p == tam){
      ip_p = 0;
      display_i = 7;
    }
  }  
}

// FUNCAO QUE PROCESSA A REQUISICAO HTTP
word processRequest(int n_rele, char job){
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
    
    // CHAMA A FUNCAO QUE ALTERA O ESTADO DO RELE
    changeRelayState(n_rele, job);
    
    // EXIBE O VALOR ATUAL DO RELE
    strcpy(output, (estadoRele[n_rele] == ON ? ON_STR : OFF_STR));
    
    // GERA A RESPOSTA DA REQUISICAO
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
   
   // INICIALIZA DISPLAY
   module.setDisplayToString("Setup", 3);
   
   // INICIALIZA PORTAS UTILIZADAS PELOS RELES
   for(int i = 0; i<QTD_RELES; i++){
     pinMode(rele[i], OUTPUT);
     digitalWrite(rele[i], LOW);
   }
   
   #if PORTA_13_ALWAYS_ON
   pinMode(13, OUTPUT);
   digitalWrite(13, HIGH);
   #endif
      
   // CARREGA BIBLIOTECA DA SHIELD ETHERNET E OBTEM IP
   Serial.println("\n[Iniciando Servidor]");
   if (ether.begin(sizeof Ethernet::buffer, mymac, 10) == 0)
      Serial.println("Falha ao acessar o controlador Ethernet.");
   #if STATIC
      ether.staticSetup(myip, gwip);
   #else
      if (!ether.dhcpSetup())
         Serial.println("DHCP falhou!");
         module.setDisplayToError();
   #endif
   
   ether.printIp("IP: ", ether.myip);
   ether.printIp("GW: ", ether.gwip);
   ether.printIp("DNS: ", ether.dnsip);
   
   setupIpOnDisplay();
   writeIpOnDisplay();
}

void loop(){
  byte keys = module.getButtons();
  
  // SE IP NAO COUBER NO DISPLAY ATUALIZA O DISPLAY FAZENDO ROTATORIA
  if(exibe_ip){
    if(tam>= 12){
      qtd_loop++;
      if (qtd_loop == LOOP_FLAG){
        writeIpOnDisplay();
        qtd_loop = 0;
      }
    }
  }
  
  // TECLA 0 DO DISPLAY
  if (keys == 1){
    changeRelayState(0, '!');
    delay(1000);
  }
  // TECLA 6 DO DISPLAY 
  if (keys == 64){
    exibe_ip = !exibe_ip;
    if(exibe_ip){
      setupIpOnDisplay();
     writeIpOnDisplay();
    }else{
      module.clearDisplay();
    }
    delay(500);
  }
  
  // TECLA 7 DO DISPLAY
  if (keys == 128) {
    Serial.println("Arduino sera reiniciado.");
    delay(200);
    resetFunc();
  }
  
  // TRATA UMA REQUISICAO DA REDE SE HOUVER
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
