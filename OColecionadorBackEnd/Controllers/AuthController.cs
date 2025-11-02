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
            var hostAcess = $"{Request.Scheme}://{Request.Host}";
            Console.WriteLine($"Host Acess: {hostAcess}");
            var decodedState = HttpUtility.UrlDecode(state);
            Console.WriteLine($"Decoded State: {decodedState}");
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
                Console.WriteLine(values.ToString());
                var content = new FormUrlEncodedContent(values);
                var response = await client.PostAsync("https://oauth2.googleapis.com/token", content);
                var tokenResponse = await response.Content.ReadFromJsonAsync<GoogleTokenResponse>();
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
