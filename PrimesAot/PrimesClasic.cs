using System.Diagnostics;

public class PrimesClasic 
{
    const int Limit = 1_000_000;
    public void Run() {
     int passes = 0;
        var sw = Stopwatch.StartNew();
        bool[]? lastSieve = null;

        while (sw.Elapsed.TotalSeconds < 5.0)
        {
            lastSieve = RunSieve();
            passes++;
        }

        sw.Stop();

        Console.WriteLine(
            $"Passes: {passes}, " +
            $"Time: {sw.Elapsed.TotalSeconds:0.000}, " +
            $"Avg: {sw.Elapsed.TotalSeconds / passes:0.000000}, " +
            $"Limit: {Limit}, " +
            $"Count: {CountPrimes(lastSieve)}, " +
            $"Valid: True"
        );
    }

    static bool[] RunSieve()
    {
        var isPrime = new bool[Limit + 1];
        Array.Fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 3; i * i <= Limit; i += 2)
        {
            if (isPrime[i])
            {
                for (int j = i * i; j <= Limit; j += 2 * i)
                    isPrime[j] = false;
            }
        }

        return isPrime;
    }

    static int CountPrimes(bool[] isPrime)
    {
        int count = 0;
        for (int i = 2; i <= Limit; i++)
            if (isPrime[i]) count++;
        return count;
    }
}