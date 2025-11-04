using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using OColecionadorBackEnd.Service;

namespace OColecionadorBackEnd.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class DockerController : ControllerBase
    {
        private readonly DockerService _dockerService;

        public DockerController(DockerService dockerService)
        {
            _dockerService = dockerService;
        }

        [HttpGet]
        public async Task<IActionResult> GetContainers()
        {
            var containers = await _dockerService.ListContainersAsync();
            return Ok(containers);
        }

        [HttpPost("start/{id}")]
        public async Task<IActionResult> Start(string id)
        {
            await _dockerService.StartContainerAsync(id);
            return Ok();
        }

        [HttpPost("stop/{id}")]
        public async Task<IActionResult> Stop(string id)
        {
            await _dockerService.StopContainerAsync(id);
            return Ok();
        }

        [HttpPost("restart/{id}")]
        public async Task<IActionResult> Restart(string id)
        {
            await _dockerService.RestartContainerAsync(id);
            return Ok();
        }
    }
}
