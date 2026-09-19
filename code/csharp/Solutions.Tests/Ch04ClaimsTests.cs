using System.Collections;
using Solutions.Claims;
using Xunit;

namespace Solutions.Tests;

/// <summary>
/// Chapter 4's C# claims, asserted. Each test names the section it backs, so
/// a claim that stops being true fails a build rather than sitting on a page.
/// </summary>
public class Ch04ClaimsTests
{
    [Fact] // 4.7: "C# truncates towards zero" -- Python's -7 // 2 is -4.
    public void IntegerDivisionTruncatesTowardsZero()
    {
        Assert.Equal(-3, Arithmetic.Divide(-7, 2));
        Assert.Equal(3, Arithmetic.Divide(7, 2));
    }

    // 4.7: C#'s % keeps the sign of the dividend; Python's keeps the
    // divisor's.
    [Fact]
    public void RemainderKeepsTheSignOfTheDividend()
    {
        Assert.Equal(-1, Arithmetic.Remainder(-7, 2));
        Assert.Equal(1, Arithmetic.Remainder(7, -2));
    }

    [Fact] // 4.7: the representation error is real in BOTH languages.
    public void ZeroPointOnePlusZeroPointTwoIsNotZeroPointThree()
    {
        Assert.False(0.1 + 0.2 == 0.3);
    }

    [Fact]
    // 4.7, CORRECTED by this test. The chapter first said C# "formats a double
    // to fifteen significant digits by default and hides it". That was true of
    // .NET Framework and of .NET Core before 3.0; since then the default
    // is the shortest round-tripping string, which is what Python prints. So
    // the two languages now agree and the difference the chapter claimed is
    // gone. The old behaviour survives as an explicit format.
    public void ADoublePrintsItsShortestRoundTrippingFormByDefault()
    {
        Assert.Equal("0.30000000000000004", Arithmetic.Default(0.1 + 0.2));
        Assert.Equal("0.3", Arithmetic.FifteenDigits(0.1 + 0.2));
    }

    [Fact] // 4.3: a record gives value equality and a hash...
    public void ARecordComparesByValueAndHashesByValue()
    {
        var a = new Reading("09:00", 12.0);
        var b = new Reading("09:00", 12.0);
        Assert.True(a == b);
        Assert.Equal(a.GetHashCode(), b.GetHashCode());
    }

    [Fact] // 4.3: ...and does NOT give you ordering. Python's order=True does.
    public void ARecordIsNotComparable()
    {
        Assert.False(new Reading("09:00", 12.0) is IComparable);
    }

    [Fact]
    // 4.2: "C# warns and continues; Python removes the capability." The type
    // still works as a dictionary key -- but the dictionary DEGRADES: an equal
    // object hashes elsewhere and cannot be found. That is the whole of the
    // difference, and it is why Python refuses instead.
    public void EqualsWithoutGetHashCodeStillWorksAndQuietlyLosesTheKey()
    {
        var stored = new EqualsOnly { Name = "db" };
        var lookup = new EqualsOnly { Name = "db" };

        var byKey = new Dictionary<EqualsOnly, int> { [stored] = 1 };

        Assert.True(stored.Equals(lookup));     // they ARE equal...
        Assert.True(byKey.ContainsKey(stored)); // ...the original is found...
        Assert.False(byKey.ContainsKey(lookup)); // ...and its equal is not.
    }
}
