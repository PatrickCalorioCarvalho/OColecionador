using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;
using System.Web;

namespace OColecionadorBackEnd.Controllers
{
    [ApiController]
    [Route("auth")]
    public class AuthController : ControllerBase
    {
        [HttpGet("callback")]
        public async Task<IActionResult> Callback([FromQuery] string code, [FromQuery] string state)
        {
            var hostdns = Request.Host.ToString();
            var scheme = Request.Headers["X-Forwarded-Proto"].FirstOrDefault() ?? Request.Scheme;
            scheme = hostdns.Contains("ngrok-free.app") ? "https" : scheme;
            var hostAcess = $"{scheme}://{hostdns}";
            var decodedState = HttpUtility.UrlDecode(state);
            var stateData = JsonSerializer.Deserialize<AuthState>(decodedState);
            var provider = stateData.Provider;
            var isMobile = stateData.Mobile;

            string token = null;

            if (provider == "github")
            {
                var client = new HttpClient();
                var values = new Dictionary<string, string>
                {
                    { "client_id", Environment.GetEnvironmentVariable("GITHUB_CLIENT_ID") ?? "" },
                    { "client_secret", Environment.GetEnvironmentVariable("GITHUB_CLIENT_SECRET") ?? "" },
                    { "code", code }
                };

                var content = new FormUrlEncodedContent(values);
                var response = await client.PostAsync("https://github.com/login/oauth/access_token", content);
                var responseString = await response.Content.ReadAsStringAsync();
                var parsed = HttpUtility.ParseQueryString(responseString);
                token = parsed["access_token"];
            }
            else if (provider == "google")
            {
                var client = new HttpClient();
                var values = new Dictionary<string, string>
                {
                    { "client_id", Environment.GetEnvironmentVariable("GOOGLE_CLIENT_ID") ?? "" },
                    { "client_secret", Environment.GetEnvironmentVariable("GOOGLE_CLIENT_SECRET") ?? "" },
                    { "code", code },
                    { "redirect_uri", $"{hostAcess}/auth/callback" },
                    { "grant_type", "authorization_code" }
                };

                var content = new FormUrlEncodedContent(values);
                var response = await client.PostAsync("https://oauth2.googleapis.com/token", content);
                var tokenResponse = await response.Content.ReadFromJsonAsync<GoogleTokenResponse>();
                if (tokenResponse == null || string.IsNullOrEmpty(tokenResponse.access_token))
                {
                    var raw = await response.Content.ReadAsStringAsync();
                    Console.WriteLine("Erro ao obter token do Google:");
                    Console.WriteLine(raw);
                    return BadRequest("Erro ao obter token.");
                }
                token = tokenResponse.access_token;
            }

            if (token == null) return BadRequest("Erro ao obter token.");

            var finalToken = $"{provider}_OC_{token}";
            var redirectUrl = isMobile
                ? $"OColecionadorMobile://auth?token={finalToken}"
                : $"{hostAcess}/authRedirect?token={finalToken}";

            return Redirect(redirectUrl);
        }

    }
    public class AuthState
    {
        public string Provider { get; set; }
        public bool Mobile { get; set; }
    }
    public class GoogleTokenResponse
    {
        public string access_token { get; set; }
        public int expires_in { get; set; }
        public string token_type { get; set; }
        public string scope { get; set; }
        public string id_token { get; set; }
    }
}
