using MediatR;

namespace BasicKube.Application.Queries
{
    public class GetTempQueryHandler : IRequestHandler<GetTempQuery, double>
    {
        private readonly IWeatherService _weather;

        public GetTempQueryHandler(IWeatherService weather)
        {
            _weather = weather;
        }

        public Task<double> Handle(GetTempQuery request, CancellationToken ct)
        {
            return _weather.GetCurrentTemperatureAsync(request.Lat, request.Lon);
        }
    }
}
