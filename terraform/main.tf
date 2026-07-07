resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_service_plan" "asp" {
  name                = var.app_service_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "app" {
  name                = var.web_app_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    always_on = true
    application_stack {
      docker_image_name = var.docker_image
      docker_registry_url = "https://ghcr.io"
    }
  }

  app_settings = {
    "WEBSITES_PORT" = "8501" # Puerto por defecto de Streamlit
    "SUPABASE_URL"  = var.supabase_url
    "SUPABASE_KEY"  = var.supabase_key
    "DATABASE_URL"  = var.database_url
  }
}

resource "azurerm_linux_web_app" "api" {
  name                = "${var.web_app_name}-api"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    always_on = true
    app_command_line = "uvicorn api:app --host 0.0.0.0 --port 8000"
    application_stack {
      docker_image_name = var.docker_image
      docker_registry_url = "https://ghcr.io"
    }
  }

  app_settings = {
    "WEBSITES_PORT" = "8000" # Puerto para FastAPI
    "SUPABASE_URL"  = var.supabase_url
    "SUPABASE_KEY"  = var.supabase_key
    "DATABASE_URL"  = var.database_url
  }
}
