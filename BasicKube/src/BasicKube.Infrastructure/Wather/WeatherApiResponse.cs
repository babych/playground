using System.Text.Json.Serialization;

using BasicKube.Application.DTO;

namespace BasicKube.Infrastructure.Wather
{
    public class WeatherApiResponse
    {
        [JsonPropertyName("current")]
        public Current Current { get; set; }
    }
}
