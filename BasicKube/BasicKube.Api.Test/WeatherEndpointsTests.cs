using System.Net;

using BasicKube.Application.Queries;

using FluentAssertions;

using Moq;

namespace BasicKube.Api.Test
{
    public class WeatherEndpointsTests
    : IClassFixture<TestApplicationFactory>
    {
        private readonly TestApplicationFactory _factory;

        public WeatherEndpointsTests(TestApplicationFactory factory)
        {
            _factory = factory;
        }

        [Fact]
        public async Task GetWind_ReturnsOk()
        {
            // Arrange
            var expected = 5.2;

            _factory.MediatorMock
                .Setup(m => m.Send(
                    It.IsAny<GetWindQuery>(),
                    It.IsAny<CancellationToken>()))
                .ReturnsAsync(expected);

            var client = _factory.CreateClient();

            // Act
            var response = await client.GetAsync("/weatherforecast/wind");

            var content = await response.Content.ReadAsStringAsync();

            // Assert
            response.StatusCode.Should().Be(HttpStatusCode.OK);
            content.Should().Be("5.2");
        }

    }
}
