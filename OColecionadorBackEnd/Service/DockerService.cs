using Docker.DotNet;
using Docker.DotNet.Models;

namespace OColecionadorBackEnd.Service
{
    public class DockerService
    {
        private readonly DockerClient _client;

        public DockerService()
        {
            var dockerUri = Environment.GetEnvironmentVariable("DOCKER_URI") ?? "unix:///var/run/docker.sock";
            _client = new DockerClientConfiguration(new Uri(dockerUri)).CreateClient();
        }

        public async Task<IList<ContainerListResponse>> ListContainersAsync()
        {
            return await _client.Containers.ListContainersAsync(new ContainersListParameters() { All = true });
        }

        public async Task StartContainerAsync(string containerId)
        {
            await _client.Containers.StartContainerAsync(containerId, null);
        }

        public async Task StopContainerAsync(string containerId)
        {
            await _client.Containers.StopContainerAsync(containerId, new ContainerStopParameters());
        }

        public async Task RestartContainerAsync(string containerId)
        {
            await _client.Containers.RestartContainerAsync(containerId, new ContainerRestartParameters());
        }
    }
}
