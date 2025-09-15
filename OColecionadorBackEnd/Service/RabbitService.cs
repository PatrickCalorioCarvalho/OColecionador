using System.Text.Json;
using RabbitMQ.Client;
using System.Text;
using Minio;

namespace OColecionadorBackEnd.Service
{
    public class RabbitService
    {
        private readonly ConnectionFactory _rabbitClient;

        public RabbitService(IConfiguration config)
        {
            var hostname = config["Rabbit:HostName"];
            var username = config["Rabbit:UserName"];
            var password = config["Rabbit:Password"];

            _rabbitClient = new ConnectionFactory()
            {
                HostName = hostname,
                UserName = username,
                Password = password
            };
        }
        public async void PublishMessage<T>(string queueName, T messageObj)
        {
            using var connection = await _rabbitClient.CreateConnectionAsync();
            using var channel = await connection.CreateChannelAsync();

            await channel.QueueDeclareAsync(
                queue: queueName,
                durable: true,
                exclusive: false,
                autoDelete: false,
                arguments: null
            );
            var json = JsonSerializer.Serialize(messageObj);
            var body = Encoding.UTF8.GetBytes(json);

            await channel.BasicPublishAsync(
                exchange: "",
                routingKey: queueName,
                body: body
            );
        }
    }
}
