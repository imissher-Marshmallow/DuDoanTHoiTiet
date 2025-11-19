#include <WiFi.h>
#include <HTTPClient.h>

// -----------------------------
// WiFi
// -----------------------------
#define WIFI_SSID      "GuessMyWifi"
#define WIFI_PASSWORD  "HahaNoob1235"

// -----------------------------
// Firebase Paths
// -----------------------------
String FB_HOST = "https://edfwef-default-rtdb.firebaseio.com";

String SENSOR_PATH   = "/water_level/sensor1.json";
String CONFIG_PATH   = "/config/sensor1.json";
String COMMAND_PATH  = "/commands/sensor1.json";

// -----------------------------
// HC-SR04 Pins
// -----------------------------
#define TRIG 5
#define ECHO 18

// -----------------------------
// Global Config
// -----------------------------
int sensorHeight   = 50;
int updateInterval = 5;
int alertThreshold = 30;

unsigned long lastConfigRead = 0;
unsigned long lastUpload = 0;

// -----------------------------
// WiFi Connect
// -----------------------------
void connectWiFi() {
  Serial.print("Connecting WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(350);
  }
  Serial.println("\nWiFi Connected!");
  Serial.println(WiFi.localIP());
}

// -----------------------------
// REST GET
// -----------------------------
String httpGet(String url) {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  HTTPClient http;
  http.begin(url);
  int code = http.GET();
  if (code != 200) {
    Serial.printf("GET error %d\n", code);
    http.end();
    return "";
  }
  String payload = http.getString();
  http.end();
  return payload;
}

// -----------------------------
// REST PUT
// -----------------------------
bool httpPut(String url, String json) {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int code = http.PUT(json);
  http.end();

  return code == 200;
}

// -----------------------------
// Read Distance
// -----------------------------
float readDistance() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(3);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(12);
  digitalWrite(TRIG, LOW);

  long dur = pulseIn(ECHO, HIGH, 30000);
  if (dur == 0) return -1;

  float dist = dur * 0.0343 / 2.0;
  return dist;
}

// -----------------------------
// Upload Sensor Data
// -----------------------------
void uploadData(float dist) {
  float water = max(0.0f, sensorHeight - dist);

  unsigned long ts = millis();

  String json = "{";
  json += "\"distance\":" + String(dist, 2) + ",";
  json += "\"waterLevel\":" + String(water, 2) + ",";
  json += "\"timestamp\":" + String(ts);
  json += "}";

  bool ok = httpPut(FB_HOST + SENSOR_PATH, json);

  if (ok)
    Serial.println("[OK] Uploaded: " + json);
  else
    Serial.println("[ERR] Upload failed");
}

// -----------------------------
// Fetch Config From Firebase
// -----------------------------
void fetchConfig() {
  String raw = httpGet(FB_HOST + CONFIG_PATH);
  if (raw.length() == 0) return;

  Serial.println("Config: " + raw);

  if (raw.indexOf("sensorHeight") > 0) {
    sensorHeight = raw.substring(raw.indexOf("sensorHeight") + 14).toInt();
  }
  if (raw.indexOf("updateInterval") > 0) {
    updateInterval = raw.substring(raw.indexOf("updateInterval") + 16).toInt();
  }
  if (raw.indexOf("alertThreshold") > 0) {
    alertThreshold = raw.substring(raw.indexOf("alertThreshold") + 16).toInt();
  }

  Serial.printf("Loaded Config: height=%d cm | interval=%d sec | alert=%d cm\n",
                sensorHeight, updateInterval, alertThreshold);
}

// -----------------------------
// Check Commands (/commands/sensor1)
// -----------------------------
void checkCommands() {
  String raw = httpGet(FB_HOST + COMMAND_PATH);
  if (raw == "null" || raw.length() < 5) return;

  Serial.println("Commands: " + raw);

  if (raw.indexOf("measure") > 0) {
    Serial.println(">>> Manual Measure Triggered!");
    float d = readDistance();
    if (d > 0) uploadData(d);
  }

  // Clear commands after handling
  httpPut(FB_HOST + COMMAND_PATH, "null");
}

// -----------------------------
// Setup
// -----------------------------
void setup() {
  Serial.begin(115200);
  delay(300);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  connectWiFi();
  fetchConfig();
}

// -----------------------------
// Loop
// -----------------------------
void loop() {

  unsigned long now = millis();

  // Poll commands
  checkCommands();

  // Read config every 10 sec
  if (now - lastConfigRead > 10000) {
    fetchConfig();
    lastConfigRead = now;
  }

  // Auto-upload
  if (now - lastUpload > updateInterval * 1000UL) {
    float dist = readDistance();
    if (dist > 0) uploadData(dist);
    else Serial.println("NO ECHO");
    lastUpload = now;
  }

  delay(50);
}
