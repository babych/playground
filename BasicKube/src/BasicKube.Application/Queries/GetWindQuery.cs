using MediatR;

namespace BasicKube.Application.Queries
{
    public class GetWindQuery : IRequest<double>
    {
        public double Lat { get; set; }
        public double Lon { get; set; }
    }

}
