using BasicKube.Application.Queries;
using BasicKube.Infrastructure.Wather;

var builder = WebApplication.CreateBuilder(args);

// Add services 
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddHttpClient<IWeatherService, WeatherService>();
builder.Services.AddMediatR(cfg =>
    cfg.RegisterServicesFromAssembly(typeof(GetTempQueryHandler).Assembly));

var app = builder.Build();

// Middleware
app.UseSwagger();
app.UseSwaggerUI();
app.UseHttpsRedirection();

// 🔹 Swagger UI
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/openapi/v1.json", "BasicKube API v1");
});

app.MapWeatherEndpoints();

app.Run();

public partial class Program { }
