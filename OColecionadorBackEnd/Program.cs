using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using OColecionadorBackEnd.Data;
using OColecionadorBackEnd.Service;

namespace OColecionadorBackEnd
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);
            builder.Services.AddDbContext<OColecionadorBackEndContext>(options =>
                options.UseSqlServer(builder.Configuration.GetConnectionString("OColecionadorBackEndContext") ?? throw new InvalidOperationException("Connection string 'OColecionadorBackEndContext' not found.")));

            builder.Services.AddScoped<MinioService>();
            builder.Services.AddScoped<RabbitService>();
            // Add services to the container.

            builder.Services.AddControllers();
            // Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            var app = builder.Build();

            using (var scope = app.Services.CreateScope())
            {
                var db = scope.ServiceProvider.GetRequiredService<OColecionadorBackEndContext>();
                db.Database.Migrate();
            }

            // Configure the HTTP request pipeline.
            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI();
            }

            app.UseAuthorization();


            app.MapControllers();

            app.Run();
        }
    }
}
