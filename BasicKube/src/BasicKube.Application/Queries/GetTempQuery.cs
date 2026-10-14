using MediatR;

namespace BasicKube.Application.Queries
{
    public class GetTempQuery : IRequest<double>
    {
        public double Lat { get; set; }
        public double Lon { get; set; }
    }
}
