namespace BasicKube.Application.Queries
{
    public interface IWeatherService
    {
        Task<double> GetCurrentTemperatureAsync(double lat, double lon);
        Task<double> GetCurrentWindAsync(double lat, double lon);
    }
}
