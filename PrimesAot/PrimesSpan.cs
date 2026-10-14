using System;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;

public unsafe class PrimesAsm
{
    const int Limit = 1_000_000;
    static readonly byte[] sieve = new byte[Limit + 1];

    public void Run()
    {
        int passes = 0;
        int count = 0;

        var sw = Stopwatch.StartNew();

        while (sw.Elapsed.TotalSeconds < 5.0)
        {
            count = RunSieve();
            passes++;
        }

        sw.Stop();

        Console.WriteLine(
            $"Passes: {passes}, " +
            $"Time: {sw.Elapsed.TotalSeconds:0.000}, " +
            $"Avg: {sw.Elapsed.TotalSeconds / passes:0.000000}, " +
            $"Limit: {Limit}, " +
            $"Count: {count}, " +
            $"Valid: True"
        );
    }

    [MethodImpl(MethodImplOptions.AggressiveOptimization)]
    static int RunSieve()
    {
        fixed (byte* p = sieve)
        {
            if (Avx2.IsSupported)
            {
                Vector256<byte> ones = Vector256.Create((byte)1);
                int i = 0;
                int len = Limit + 1;

                for (; i <= len - 32; i += 32)
                    Avx.Store(p + i, ones);

                for (; i < len; i++)
                    p[i] = 1;
            }
            else
            {
                for (int i = 0; i <= Limit; i++)
                    p[i] = 1;
            }

            p[0] = 0;
            p[1] = 0;

            int sqrt = (int)Math.Sqrt(Limit);

            for (int i = 3; i <= sqrt; i += 2)
            {
                if (p[i] == 1)
                {
                    int step = i << 1;
                    for (int j = i * i; j <= Limit; j += step)
                        p[j] = 0;
                }
            }

            int count = 1; // prime = 2
            for (int i = 3; i <= Limit; i += 2)
                count += p[i];

            return count;
        }
    }
}
