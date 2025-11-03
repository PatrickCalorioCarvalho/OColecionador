using System.Net.Http.Headers;
using System.Text.Json;

namespace OColecionadorBackEnd.Middlewares
{
    public class OAuthMiddleware
    {
        private readonly RequestDelegate _next;

        public OAuthMiddleware(RequestDelegate next)
        {
            _next = next;
        }
        public async Task Invoke(HttpContext context)
        {
            var path = context.Request.Path.Value;

            if (!path.StartsWith("/api", StringComparison.OrdinalIgnoreCase))
            {
                await _next(context);
                return;
            }

            var authHeader = context.Request.Headers["Authorization"].FirstOrDefault();
            if (string.IsNullOrEmpty(authHeader) || !authHeader.StartsWith("Bearer "))
            {
                context.Response.StatusCode = 401;
                await context.Response.WriteAsync("Token ausente ou inválido");
                return;
            }

            var rawToken = authHeader.Substring("Bearer ".Length).Trim();
            var parts = rawToken.Split("_OC_");
            if (parts.Length != 2)
            {
                context.Response.StatusCode = 401;
                await context.Response.WriteAsync("Formato de token inválido");
                return;
            }

            var tipo = parts[0];
            var token = parts[1];
            string? clientId = null;

            if (tipo == "google")
                clientId = await GetGoogleUserId(token);
            else if (tipo == "github")
                clientId = await GetGitHubUserId(token);

            if (clientId == null)
            {
                context.Response.StatusCode = 401;
                await context.Response.WriteAsync("Token inválido ou falha ao gerar ID");
                return;
            }

            context.Request.Headers["X-Client"] = clientId;
            await _next(context);
        }


        public async Task<string?> GetGoogleUserId(string token)
        {
            var client = new HttpClient();
            var response = await client.GetAsync($"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}");
            if (!response.IsSuccessStatusCode) return null;

            var json = await response.Content.ReadAsStringAsync();
            var data = JsonSerializer.Deserialize<JsonElement>(json);

            string email = data.TryGetProperty("email", out var emailProp) ? emailProp.GetString() ?? "noemail" : "noemail";
            string name = data.TryGetProperty("name", out var nameProp) ? nameProp.GetString() ?? "unknown" : "unknown";

            return $"{name}_{email}_google";
        }

        public async Task<string?> GetGitHubUserId(string token)
        {
            var client = new HttpClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            client.DefaultRequestHeaders.UserAgent.ParseAdd("YourAppName");

            var response = await client.GetAsync("https://api.github.com/user");
            if (!response.IsSuccessStatusCode) return null;

            var json = await response.Content.ReadAsStringAsync();
            var data = JsonSerializer.Deserialize<JsonElement>(json);

            string login = data.TryGetProperty("login", out var loginProp) ? loginProp.GetString() ?? "unknown" : "unknown";
            string email = data.TryGetProperty("email", out var emailProp) ? emailProp.GetString() ?? "noemail" : "noemail";

            return $"{login}_{email}_github";
        }


    }
}
