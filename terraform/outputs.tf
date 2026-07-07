output "webapp_url" {
  value       = azurerm_linux_web_app.app.default_hostname
  description = "The default hostname of the web app."
}

output "api_url" {
  value       = azurerm_linux_web_app.api.default_hostname
  description = "The default hostname of the API app."
}
