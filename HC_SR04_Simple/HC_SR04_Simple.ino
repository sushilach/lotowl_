#include <HCSR04.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>



const char* ssid = "YSU_event_HackYSU";
const char* password = "HackYSU2026!";

const char* URL = "https://app.lotowl.info/update";


int triggerPin = D0;
int echoPin = D1;
int inRange = 0;
int maxLim = 200;
int targetTime = 3;
int deviceId = 1;
unsigned long initTime;
int buttonPin = D2;
bool pressed;


void setup () {
  Serial.begin(9600);
  HCSR04.begin(triggerPin, echoPin);
  pinMode(buttonPin, INPUT_PULLUP);
  WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");


}

void sendData(int deviceId, float accur) {

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    WiFiClientSecure client;

    // For quick testing against hosted HTTPS. Replace with cert pinning for production.
    client.setInsecure();

    http.setTimeout(10000);
    http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
    http.begin(client, URL);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"deviceId\":" + String(deviceId) +
                  ",\"accuracy\":" + String(accur) + "}";

    int responseCode = http.POST(json);
    String responseBody = http.getString();

    Serial.print("HTTP Response code: ");
    Serial.println(responseCode);
    if (responseCode < 0) {
      Serial.print("HTTP Error: ");
      Serial.println(http.errorToString(responseCode));
      Serial.print("WiFi status: ");
      Serial.println(WiFi.status());
      Serial.print("Local IP: ");
      Serial.println(WiFi.localIP());
    }
    Serial.print("Response body: ");
    Serial.println(responseBody);

    http.end();
  }
  else {
    Serial.println("WiFi not connected");
  }
}



void loop () {
int buttonState = digitalRead(buttonPin);
  // Serial.print("button state: ");
  // Serial.println(buttonState);
  
  int currentState = buttonState;

if (currentState == LOW) {
   deviceId = 1;
    // Serial.println("PRESSED");
  } else {
    // Serial.println("not pressed");
    deviceId = 2;
  }

// debug only
  // Serial.print("Device ID: ");
  // Serial.println(deviceId);

  double* distances = HCSR04.measureDistanceCm();
  
  delay(250);


  int dist = distances[0];

  if (dist == -1) {
    dist = 1000;
  }
  Serial.println(dist);
  if (dist<=maxLim && inRange == 0) {
    Serial.println("first");
    initTime = millis();
    inRange = 1;
  }

  if(inRange == 1 && (dist>maxLim || dist==-1)) {
    // calc accuracy
    Serial.println("second");
    float timeTaken = (millis() - initTime) / 1000;
    float accur = 1 - (abs(targetTime - timeTaken) * .25);

    Serial.println("Device ID: " + String(deviceId));
    Serial.println(String(accur * 100) + "%");


    // send device id and accuracy to backend
    sendData(deviceId, accur);
    inRange = 0;
  }

}

