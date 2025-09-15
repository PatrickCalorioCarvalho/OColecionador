using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Policy;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using OColecionadorBackEnd.Data;
using OColecionadorBackEnd.Model;
using OColecionadorBackEnd.Service;

namespace OColecionadorBackEnd.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ItemsController : ControllerBase
    {
        private readonly OColecionadorBackEndContext _context;
        private readonly MinioService _minio;
        private readonly RabbitService _rabbit;
        public ItemsController(OColecionadorBackEndContext context, MinioService minio, RabbitService rabbit)
        {
            _context = context;
            _minio = minio;
            _rabbit = rabbit;
        }

        // GET: api/Items
        [HttpGet]
        public async Task<ActionResult> GetItem()
        {
            var items = await _context.Item
                .Include(i => i.Fotos)
                .ToListAsync();

            var result = new List<object>();

            foreach (var item in items)
            {
                var fotosComUrls = new List<string>();

                if(!item.Fotos.IsNullOrEmpty())
                {
                    foreach (var foto in item.Fotos)
                    {
                        var url = await _minio.GetPresignedUrlAsync(foto.Caminho);
                        fotosComUrls.Add(url);
                    }
                }
                result.Add(new
                {
                    item.Id,
                    item.Nome,
                    item.CategoriaId,
                    Fotos = fotosComUrls
                });
            }

            return Ok(result);
        }

        // GET: api/Items/5
        [HttpGet("{id}")]
        public async Task<ActionResult> GetItem(int id)
        {
            var item = await _context.Item
                .Include(i => i.Fotos)
                .FirstOrDefaultAsync(i => i.Id == id);

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

            var result = new
            {
                item.Id,
                item.Nome,
                item.CategoriaId,
                Fotos = fotosComUrls
            };

            return Ok(result);
        }

        // PUT: api/Items/5
        // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
        [HttpPut("{id}")]
        public async Task<IActionResult> PutItem(int id, Item item)
        {
            if (id != item.Id)
            {
                return BadRequest();
            }

            _context.Entry(item).State = EntityState.Modified;

            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!ItemExists(id))
                {
                    return NotFound();
                }
                else
                {
                    throw;
                }
            }

            return NoContent();
        }

        // POST: api/Items
        // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
        [HttpPost]
        public async Task<IActionResult> PostItem(
                [FromForm] int categoriaId,
                [FromForm] string nome,
                [FromForm] List<IFormFile> fotos)
        {
            if (string.IsNullOrWhiteSpace(nome))
                return BadRequest("Nome do item é obrigatório.");

            if (!_context.Categoria.Any(c => c.Id == categoriaId))
                return NotFound($"Categoria {categoriaId} não encontrada.");

            // cria o item
            var item = new Item
            {
                Nome = nome,
                CategoriaId = categoriaId,
                Fotos = new List<Foto>()
            };

            // faz upload das fotos para o MinIO
            foreach (var arquivo in fotos ?? Enumerable.Empty<IFormFile>())
            {
                var fileName = Guid.NewGuid() + Path.GetExtension(arquivo.FileName);
                using var stream = arquivo.OpenReadStream();
                var url = await _minio.UploadFotoAsync(stream, fileName);
                item.Fotos.Add(new Foto
                {
                    Caminho = url
                });
            }

            // salva no banco
            _context.Item.Add(item);
            await _context.SaveChangesAsync();

            foreach(Foto f in item.Fotos )
            {
                var message = new FotoMessage
                {
                    ItemId = item.Id,
                    Categoria = _context.Categoria.Where(c => c.Id == item.CategoriaId).First().Descricao,
                    Caminho = f.Caminho
                };
                _rabbit.PublishMessage<FotoMessage>("ImageAugmentations", message);
            }
            

            return Ok(new
            {
                item.Id,
                item.Nome,
                item.CategoriaId,
                Fotos = item.Fotos.Select(f => f.Caminho).ToList()
            });
        }

        // DELETE: api/Items/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteItem(int id)
        {
            var item = await _context.Item.FindAsync(id);
            if (item == null)
            {
                return NotFound();
            }

            _context.Item.Remove(item);
            await _context.SaveChangesAsync();

            return NoContent();
        }

        private bool ItemExists(int id)
        {
            return _context.Item.Any(e => e.Id == id);
        }
    }
}
