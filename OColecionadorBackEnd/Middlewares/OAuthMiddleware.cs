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
            Console.WriteLine($"Tipo de token: {tipo}");
            Console.WriteLine($"Token: {token}");
            dynamic userData = null;

            if (tipo == "google")
                userData = await GetGoogleUser(token);
            else if (tipo == "github")
                userData = await GetGitHubUser(token);
            else
            {
                context.Response.StatusCode = 401;
                await context.Response.WriteAsync("Tipo de token desconhecido");
                return;
            }
            Console.WriteLine($"Dados do usuário: {userData}");
            if (userData == null)
            {
                context.Response.StatusCode = 401;
                await context.Response.WriteAsync("Token inválido");
                return;
            }

            // ✅ Gerar ID do usuário
            string username = userData.name ?? userData.login ?? "unknown";
            string email = userData.email ?? "noemail";
            string clientId = $"{username}_{email}_{tipo}";
            Console.WriteLine($"Client ID gerado: {clientId}");

            // ✅ Adicionar no header da requisição
            context.Request.Headers["X-Client"] = clientId;

            await _next(context);
        }

        public async Task<dynamic> GetGoogleUser(string token)
        {
            var client = new HttpClient();
            var response = await client.GetAsync($"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}");
            if (!response.IsSuccessStatusCode) return null;
            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(json);
        }

        public async Task<dynamic> GetGitHubUser(string token)
        {
            var client = new HttpClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            client.DefaultRequestHeaders.UserAgent.ParseAdd("YourAppName");
            var response = await client.GetAsync("https://api.github.com/user");
            if (!response.IsSuccessStatusCode) return null;
            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(json);
        }

    }
}
