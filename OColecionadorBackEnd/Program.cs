using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.Extensions.DependencyInjection;
using OColecionadorBackEnd.Data;
using OColecionadorBackEnd.Service;
using OColecionadorBackEnd.Middlewares;
using System.Reflection.PortableExecutable;

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

            app.UseForwardedHeaders(new ForwardedHeadersOptions
            {
                ForwardedHeaders = ForwardedHeaders.XForwardedProto | ForwardedHeaders.XForwardedHost
            });

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

            app.UseMiddleware<OAuthMiddleware>();

            app.MapControllers();

            app.Run();
        }
    }
}
