using MediatR;

namespace BasicKube.Application.Queries
{
    public class GetWindQueryHandler : IRequestHandler<GetWindQuery, double>
    {
        private readonly IWeatherService _weather;

        public GetWindQueryHandler(IWeatherService weather)
        {
            _weather = weather;
        }

        public Task<double> Handle(GetWindQuery request, CancellationToken cancellationToken)
        {
            return _weather.GetCurrentWindAsync(request.Lat, request.Lon);
        }
    }
}
