using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Minio.DataModel;
using Newtonsoft.Json;
using OColecionadorBackEnd.Data;
using OColecionadorBackEnd.Model;
using OColecionadorBackEnd.Service;
using System.ComponentModel.DataAnnotations;
using System.Net.Http;
using System.Net.Http.Headers;

namespace OColecionadorBackEnd.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ClasificarController : ControllerBase
    {
        private readonly OColecionadorBackEndContext _context;
        private readonly MinioService _minio;
        private readonly IHttpClientFactory _httpClientFactory;
        public ClasificarController(OColecionadorBackEndContext context, MinioService minio, IHttpClientFactory httpClientFactory)
        {
            _context = context;
            _httpClientFactory = httpClientFactory;
            _minio = minio;
        }

        [HttpPost]
        public async Task<IActionResult> PostClasificar([FromForm] UploadClasificar uploadClasificar)
        {
            if (uploadClasificar.Foto == null || uploadClasificar.Foto.Length == 0)
                return BadRequest("Arquivo não enviado.");

            var client = _httpClientFactory.CreateClient();

            using var content = new MultipartFormDataContent();
            using var stream = uploadClasificar.Foto.OpenReadStream();
            using var fileContent = new StreamContent(stream);

            fileContent.Headers.ContentType = new MediaTypeHeaderValue(uploadClasificar.Foto.ContentType);
            content.Add(fileContent, "file", uploadClasificar.Foto.FileName);

            var response = await client.PostAsync("http://ocolecionadorclassifier:5001/api/classify", content);

            if (!response.IsSuccessStatusCode)
                return StatusCode((int)response.StatusCode, "Erro ao classificar imagem.");

            var json = await response.Content.ReadAsStringAsync();
            var resultado = JsonConvert.DeserializeObject<ClassificacaoResponse>(json);
            var items = new List<object>();

            foreach (var s in resultado.Semelhantes)
            {

                var item = await _context.Item
                    .Include(i => i.Fotos)
                    .Where(i => i.Fotos.Any(f => f.Caminho == s.Item))
                    .FirstOrDefaultAsync();

                if (item == null)
                    return NotFound();

                var fotosComUrls = new List<string>();

                if (!item.Fotos.IsNullOrEmpty())
                {
                    foreach (var foto in item.Fotos)
                    {
                        var url = await _minio.GetPresignedUrlAsync(foto.Caminho);
                        fotosComUrls.Add(url);
                    }
                }
                if (!items.Any(i => ((dynamic)i).Id == item.Id))
                {
                    items.Add(new
                    {
                        item.Id,
                        item.Nome,
                        item.CategoriaId,
                        s.Distancia,
                        Fotos = fotosComUrls
                    });
                }
            }

            var result = new
            {
                resultado.Classe,
                resultado.Confianca,
                Items = items
            };

            return Ok(result);
        }
    }
    public class UploadClasificar
    {
        public required IFormFile Foto { get; set; }
    }
    public class ClassificacaoResponse
    {
        public string Classe { get; set; }
        public float Confianca { get; set; }
        public List<Semelhante> Semelhantes { get; set; }
    }
    public class Semelhante
    {
        public string Item { get; set; }
        public float Distancia { get; set; }
    }
}
