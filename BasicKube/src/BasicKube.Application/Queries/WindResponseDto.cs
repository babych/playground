using System.Text.Json.Serialization;

namespace BasicKube.Application.Queries
{
    public class WindResponseDto
    {
        [JsonPropertyName("current")]
        public CurrentWeather Current { get; set; } = default!;
    }
}
