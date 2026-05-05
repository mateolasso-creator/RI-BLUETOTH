#include <string.h>
#include "esp_log.h"
#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_bt_device.h"
#include "esp_gap_bt_api.h"
#include "esp_spp_api.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_http_client.h"
#include "cJSON.h"
#include <driver/gpio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"

// ========================================================
// CONFIGURACIÓN - CAMBIA ESTO
// ========================================================
#define SSID "Jenny"
#define PASSWORD "0103589313"
#define SERVER "http://192.168.1.100:8088" // IP de tu PC y puerto de Docker
// ========================================================

#define LED_R 25
#define LED_G 26
#define LED_B 27
#define BUZZER 32
#define DEVICE_NAME "ESP32-Acceso-BT"

static const char *TAG = "BT_ACC";

static void set_led(bool r, bool g, bool b) {
    gpio_set_level(LED_R, r);
    gpio_set_level(LED_G, g);
    gpio_set_level(LED_B, b);
}

static void beep(uint32_t ms) {
    gpio_set_level(BUZZER, 1);
    vTaskDelay(pdMS_TO_TICKS(ms));
    gpio_set_level(BUZZER, 0);
}

// ---- Verificar acceso vía HTTP ----
static bool verificar_acceso(const char *token) {
    char url[128];
    // Ajustado para tu servidor PHP: api.php?token=...
    snprintf(url, sizeof(url), "%s/api.php?token=%s", SERVER, token);
    
    char buf[512] = {0};
    esp_http_client_config_t cfg = {
        .url = url,
        .user_data = buf,
        .buffer_size_tx = 512,
    };
    
    esp_http_client_handle_t c = esp_http_client_init(&cfg);
    esp_err_t err = esp_http_client_perform(c);
    
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Respuesta recibida: %s", buf);
        cJSON *root = cJSON_Parse(buf);
        if (root) {
            cJSON *status = cJSON_GetObjectItem(root, "status");
            bool autorizado = (status && strcmp(status->valuestring, "GRANTED") == 0);
            cJSON_Delete(root);
            esp_http_client_cleanup(c);
            return autorizado;
        }
    }
    
    esp_http_client_cleanup(c);
    return false;
}

// ---- Callback Bluetooth SPP ----
static void spp_callback(esp_spp_cb_event_t event, esp_spp_cb_param_t *param) {
    switch (event) {
        case ESP_SPP_INIT_EVT:
            esp_bt_dev_set_device_name(DEVICE_NAME);
            esp_bt_gap_set_scan_mode(ESP_BT_CONNECTABLE, ESP_BT_GENERAL_DISCOVERABLE);
            esp_spp_start_srv(ESP_SPP_SEC_AUTHENTICATE, ESP_SPP_ROLE_SLAVE, 0, "SPP_SERVER");
            break;
        case ESP_SPP_SRV_OPEN_EVT:
            ESP_LOGI(TAG, "Smartphone conectado por Bluetooth");
            set_led(1, 1, 1); // Blanco: Procesando
            break;
        case ESP_SPP_DATA_IND_EVT: {
            char token[64] = {0};
            int len = param->data_ind.len < 63 ? param->data_ind.len : 63;
            memcpy(token, param->data_ind.data, len);
            
            // Limpiar saltos de línea del token recibido
            for(int i=0; i<len; i++) {
                if(token[i] == '\r' || token[i] == '\n') token[i] = '\0';
            }

            ESP_LOGI(TAG, "Token recibido desde App: %s", token);
            
            bool ok = verificar_acceso(token);
            const char *resp;

            if (ok) {
                ESP_LOGI(TAG, "¡ACCESO CONCEDIDO!");
                set_led(0, 1, 0); // Verde
                beep(200);
                resp = "ACCESO CONCEDIDO\n";
            } else {
                ESP_LOGI(TAG, "ACCESO DENEGADO");
                set_led(1, 0, 0); // Rojo
                beep(600);
                resp = "ACCESO DENEGADO\n";
            }
            
            esp_spp_write(param->data_ind.handle, strlen(resp), (uint8_t *)resp);
            vTaskDelay(pdMS_TO_TICKS(2000));
            set_led(0, 0, 1); // Azul: Esperando de nuevo
            break;
        }
        case ESP_SPP_CLOSE_EVT:
            ESP_LOGI(TAG, "Smartphone desconectado");
            set_led(0, 0, 1);
            break;
        default: break;
    }
}

void app_main(void) {
    // Configurar Pines
    gpio_config_t io = {
        .pin_bit_mask = (1ULL<<LED_R)|(1ULL<<LED_G)|(1ULL<<LED_B)|(1ULL<<BUZZER),
        .mode = GPIO_MODE_OUTPUT
    };
    gpio_config(&io);
    set_led(1, 1, 0); // Amarillo: Iniciando

    // Inicializaciones
    nvs_flash_init();
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_create_default_wifi_sta();

    // Conectar Wi-Fi
    wifi_init_config_t wcfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&wcfg);
    wifi_config_t wsta = { .sta = { .ssid = SSID, .password = PASSWORD } };
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wsta);
    esp_wifi_start();
    esp_wifi_connect();
    
    ESP_LOGI(TAG, "Conectando a WiFi...");
    vTaskDelay(pdMS_TO_TICKS(5000)); 

    // Inicializar Bluetooth
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    esp_bt_controller_init(&bt_cfg);
    esp_bt_controller_enable(ESP_BT_MODE_CLASSIC_BT);
    esp_bluedroid_init();
    esp_bluedroid_enable();
    esp_spp_register_callback(spp_callback);
    esp_spp_init(ESP_SPP_MODE_CB);

    set_led(0, 0, 1); // Azul: Listo para recibir conexión
    ESP_LOGI(TAG, "Sistema listo. Esperando conexión Bluetooth...");
}