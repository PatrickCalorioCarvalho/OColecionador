using System.Net.Http.Headers;

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

            var rawToken = authHeader.Substring("Bearer ".Length);

            var parts = rawToken.Split("_OC_", 2);
            if (parts.Length != 2)
            {
                context.Response.StatusCode = 401;
                await context.Response.WriteAsync("Formato de token inválido");
                return;
            }

            var tipo = parts[0];
            var token = parts[1];
            bool isValid = false;

            if (tipo == "google")
                isValid = await ValidateGoogleToken(token);
            else if (tipo == "github")
                isValid = await ValidateGitHubToken(token);
            else
            {
                context.Response.StatusCode = 401;
                await context.Response.WriteAsync("Tipo de token desconhecido");
                return;
            }

            if (!isValid)
            {
                context.Response.StatusCode = 401;
                await context.Response.WriteAsync("Token inválido");
                return;
            }

            await _next(context);
        }
        public async Task<bool> ValidateGoogleToken(string token)
        {
            var client = new HttpClient();
            var response = await client.GetAsync($"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}");
            return response.IsSuccessStatusCode;
        }

        public async Task<bool> ValidateGitHubToken(string token)
        {
            var client = new HttpClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            var response = await client.GetAsync("https://api.github.com/user");
            return response.IsSuccessStatusCode;
        }

    }
}
