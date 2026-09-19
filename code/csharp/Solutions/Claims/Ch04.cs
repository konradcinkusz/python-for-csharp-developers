// The C# half of Chapter 4's comparisons, as code rather than as prose.
//
// Every claim this book makes about C# is the one a reader is most likely to
// know better than the author, and two have already been wrong. These types
// exist so the claims are compiled and asserted rather than remembered, and
// Solutions.Tests/Ch04ClaimsTests.cs is where each is checked.

namespace Solutions.Claims;

/// <summary>
/// Chapter 4 section 4.3: what a record gives you, and what it does not.
/// </summary>
public record Reading(string TakenAt, double Celsius);

/// <summary>
/// Chapter 4 section 4.2: overriding Equals and not GetHashCode.
///
/// C# raises CS0659 here -- a warning, not an error -- and the type keeps
/// working. That is the contrast the chapter draws: Python sets __hash__ to
/// None and removes the capability outright. The warning is suppressed at
/// the project level, because raising it IS the demonstration.
/// </summary>
public class EqualsOnly
{
    public string Name { get; init; } = "";

    public override bool Equals(object? other) =>
        other is EqualsOnly e && e.Name == Name;
}

/// <summary>
/// Chapter 4 section 4.7: integer division, and how a double prints.
/// </summary>
public static class Arithmetic
{
    /// <summary>
    /// C# truncates towards zero where Python's // floors.
    /// </summary>
    public static int Divide(int a, int b) => a / b;

    /// <summary>
    /// C#'s % takes the sign of the dividend, where Python's % takes the
    /// sign of the divisor.
    /// </summary>
    public static int Remainder(int a, int b) => a % b;

    /// <summary>
    /// What ToString() actually prints for a double on this runtime.
    ///
    /// Since .NET Core 3.0 this is the SHORTEST ROUND-TRIPPING string, which
    /// is what Python has always printed. Before that it was fifteen
    /// significant digits, which hid the representation error -- and that
    /// older behaviour is still reachable, as G15 below.
    /// </summary>
    public static string Default(double value) => value.ToString();

    /// <summary>
    /// The pre-.NET-Core-3.0 default, kept so the change is visible.
    /// </summary>
    public static string FifteenDigits(double value) => value.ToString("G15");
}
