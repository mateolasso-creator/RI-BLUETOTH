idf_component_register(SRCS "main.c"
                    INCLUDE_DIRS "."
                    PRIV_REQUIRES nvs_flash esp_wifi esp_http_client bt esp_event cjson driver esp_driver_gpio)