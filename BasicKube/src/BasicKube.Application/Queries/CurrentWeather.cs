using System.Text.Json.Serialization;

namespace BasicKube.Application.Queries
{
    public class CurrentWeather
    {
        [JsonPropertyName("wind_speed_10m")]
        public double WindSpeed10m { get; set; }
    }
}
