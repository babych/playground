using System.Text.Json.Serialization;

namespace BasicKube.Application.DTO
{
    public class Current
    {
        [JsonPropertyName("time")]
        public DateTime Time { get; set; }

        [JsonPropertyName("temperature_2m")]
        public double Temperature_2m { get; set; }
    }
}
