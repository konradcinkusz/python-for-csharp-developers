// Appendix D's twenty problems, the C# half.
//
// These are printed beside the Python solutions so a reader can see which
// habits carry across and which do not. They are compiled and tested in
// CI for the reason the whole appendix exists: a worked answer nobody
// runs is the class of claim this book refuses.
//
// Where the C# is longer, it is longer because the standard library has
// nothing for the step, not because it was written carelessly.

namespace Solutions.Interview;

public static class Problems
{
    // --8<-- [start:twosum]
    // D.1. Dictionary is the index. TryGetValue does in one call what
    // Python needs `in` plus a lookup for.
    public static (int, int)? TwoSum(IReadOnlyList<int> nums, int target)
    {
        var seen = new Dictionary<int, int>();
        for (var i = 0; i < nums.Count; i++)
        {
            if (seen.TryGetValue(target - nums[i], out var j))
                return (j, i);
            seen[nums[i]] = i;
        }
        return null;
    }
    // --8<-- [end:twosum]

    // --8<-- [start:anagrams]
    // D.2. Same shape, and the same ordering subtlety: each group is
    // sorted before the groups are compared.
    public static List<List<string>> GroupAnagrams(
        IEnumerable<string> words) =>
        words.GroupBy(w => new string(w.OrderBy(c => c).ToArray()))
             .Select(g => g.OrderBy(w => w, StringComparer.Ordinal)
                           .ToList())
             .OrderBy(g => g[0], StringComparer.Ordinal)
             .ToList();
    // --8<-- [end:anagrams]

    // --8<-- [start:firstunique]
    // D.3. FirstOrDefault returns null for a reference type, so the
    // nullable char has to be spelled out.
    public static char? FirstUnique(string text)
    {
        var counts = text.GroupBy(c => c)
                         .ToDictionary(g => g.Key, g => g.Count());
        foreach (var c in text)
            if (counts[c] == 1)
                return c;
        return null;
    }
    // --8<-- [end:firstunique]

    // --8<-- [start:merge]
    // D.4. Tuples compare element by element here too, so OrderBy needs
    // no comparer -- and being immutable, the running span is replaced.
    public static List<(int Low, int High)> MergeIntervals(
        IEnumerable<(int Low, int High)> spans)
    {
        var merged = new List<(int Low, int High)>();
        foreach (var (low, high) in spans.OrderBy(s => s))
        {
            if (merged.Count > 0 && low <= merged[^1].High)
                merged[^1] = (merged[^1].Low, Math.Max(merged[^1].High, high));
            else
                merged.Add((low, high));
        }
        return merged;
    }
    // --8<-- [end:merge]

    // --8<-- [start:balanced]
    // D.5. Stack<T> exists here, which is the one place in this appendix
    // where C# has the type and Python uses a list.
    private static readonly Dictionary<char, char> Closers =
        new() { [')'] = '(', [']'] = '[', ['}'] = '{' };

    public static bool Balanced(string text)
    {
        var stack = new Stack<char>();
        foreach (var c in text)
        {
            if (Closers.ContainsValue(c))
                stack.Push(c);
            else if (Closers.TryGetValue(c, out var open))
                if (stack.Count == 0 || stack.Pop() != open)
                    return false;
        }
        return stack.Count == 0;
    }
    // --8<-- [end:balanced]

    // --8<-- [start:dedupe]
    // D.6. Distinct() preserves order in practice but does not promise
    // to; Python's dict.fromkeys promises it.
    public static List<T> Dedupe<T>(IEnumerable<T> items) =>
        items.Distinct().ToList();
    // --8<-- [end:dedupe]

    // --8<-- [start:chunk]
    // D.7. Chunk arrived in .NET 6. Before that this was a loop.
    public static List<T[]> Chunk<T>(IReadOnlyList<T> items, int size)
    {
        if (size < 1)
            throw new ArgumentOutOfRangeException(
                nameof(size), size, "size must be positive");
        return items.Chunk(size).ToList();
    }
    // --8<-- [end:chunk]

    // --8<-- [start:transpose]
    // D.8. No splat, so the transpose indexes. The ragged check that
    // Python gets from zip(strict=True) is written by hand.
    public static List<List<int>> Transpose(
        IReadOnlyList<IReadOnlyList<int>> m)
    {
        if (m.Count == 0) return [];
        var width = m[0].Count;
        if (m.Any(row => row.Count != width))
            throw new ArgumentException("ragged matrix", nameof(m));
        return Enumerable.Range(0, width)
                         .Select(c => m.Select(row => row[c]).ToList())
                         .ToList();
    }
    // --8<-- [end:transpose]

    // --8<-- [start:flatten]
    // D.9. The recursive iterator, which is `yield from` with more words.
    public static IEnumerable<int> Flatten(IEnumerable<object> nested)
    {
        foreach (var item in nested)
        {
            if (item is IEnumerable<object> inner)
                foreach (var leaf in Flatten(inner))
                    yield return leaf;
            else
                yield return (int)item;
        }
    }
    // --8<-- [end:flatten]

    // --8<-- [start:topwords]
    // D.10. GroupBy, OrderByDescending, Take -- which is what
    // Counter.most_common is, spelled out.
    public static List<(string Word, int Count)> TopWords(
        string text, int n) =>
        System.Text.RegularExpressions.Regex
            .Matches(text.ToLowerInvariant(), "[a-z']+")
            .Select(m => m.Value)
            .GroupBy(w => w)
            .OrderByDescending(g => g.Count())
            .ThenBy(g => g.Key, StringComparer.Ordinal)
            .Take(n)
            .Select(g => (g.Key, g.Count()))
            .ToList();
    // --8<-- [end:topwords]

    // --8<-- [start:binarysearch]
    // D.11. BinarySearch returns the bitwise complement of the insertion
    // point when the value is absent, which is the sign test people get
    // wrong. bisect returns the insertion point and asks you to look.
    public static int IndexOf(int[] sortedItems, int value)
    {
        var i = Array.BinarySearch(sortedItems, value);
        return i < 0 ? -1 : i;
    }
    // --8<-- [end:binarysearch]

    // --8<-- [start:runningtotal]
    // D.12. No Aggregate that yields the intermediates, so a local.
    public static List<int> RunningTotal(IEnumerable<int> amounts)
    {
        var total = 0;
        var output = new List<int>();
        foreach (var amount in amounts)
        {
            total += amount;
            output.Add(total);
        }
        return output;
    }
    // --8<-- [end:runningtotal]

    // --8<-- [start:rotate]
    // D.13. C#'s % keeps the sign of the DIVIDEND, so a negative rotation
    // needs the correction Python's % does for you.
    public static List<T> Rotate<T>(IReadOnlyList<T> items, int by)
    {
        if (items.Count == 0) return [];
        by = ((by % items.Count) + items.Count) % items.Count;
        return [.. items.Skip(by), .. items.Take(by)];
    }
    // --8<-- [end:rotate]

    // --8<-- [start:commonprefix]
    // D.14. Min and max over strings, same as Python.
    public static string LongestCommonPrefix(IReadOnlyList<string> words)
    {
        if (words.Count == 0) return "";
        var first = words.Min(StringComparer.Ordinal)!;
        var last = words.Max(StringComparer.Ordinal)!;
        for (var i = 0; i < first.Length; i++)
            if (i >= last.Length || last[i] != first[i])
                return first[..i];
        return first;
    }
    // --8<-- [end:commonprefix]

    // --8<-- [start:palindrome]
    // D.15. No slice-reverse, so Reverse() then SequenceEqual.
    public static bool IsPalindrome(string text)
    {
        var cleaned = text.Where(char.IsLetterOrDigit)
                          .Select(char.ToLowerInvariant)
                          .ToList();
        return cleaned.SequenceEqual(Enumerable.Reverse(cleaned));
    }
    // --8<-- [end:palindrome]

    // --8<-- [start:deepget]
    // D.16. The dictionary walk, with the same guard against walking
    // into something that is not a dictionary.
    public static object? DeepGet(
        object? data, string path, object? fallback = null)
    {
        foreach (var key in path.Split('.'))
        {
            if (data is not IReadOnlyDictionary<string, object?> dict
                || !dict.TryGetValue(key, out var next))
                return fallback;
            data = next;
        }
        return data;
    }
    // --8<-- [end:deepget]

    // --8<-- [start:dedupeby]
    // D.17. DistinctBy, since .NET 6.
    public static List<T> DedupeBy<T, TKey>(
        IEnumerable<T> items, Func<T, TKey> key) =>
        items.DistinctBy(key).ToList();
    // --8<-- [end:dedupeby]

    // --8<-- [start:latest]
    // D.18. GroupBy builds every group before discarding all but one of
    // each; the dictionary version does not.
    public static List<T> LatestPerKey<T>(
        IEnumerable<T> rows, Func<T, string> key, Func<T, int> when)
    {
        var best = new Dictionary<string, T>();
        foreach (var row in rows)
            if (!best.TryGetValue(key(row), out var held)
                || when(row) > when(held))
                best[key(row)] = row;
        return best.OrderBy(kv => kv.Key, StringComparer.Ordinal)
                   .Select(kv => kv.Value)
                   .ToList();
    }
    // --8<-- [end:latest]

    // --8<-- [start:pairwisediff]
    // D.19. No pairwise in the BCL, so Zip with a Skip(1).
    public static List<int> PairwiseDiff(IEnumerable<int> readings)
    {
        var list = readings.ToList();
        return list.Zip(list.Skip(1), (a, b) => b - a).ToList();
    }
    // --8<-- [end:pairwisediff]

    // --8<-- [start:partition]
    // D.20. Two Wheres walk the input twice; this walks it once.
    public static (List<T> Matching, List<T> Others) Partition<T>(
        IEnumerable<T> items, Func<T, bool> predicate)
    {
        List<T> matching = [], others = [];
        foreach (var item in items)
            (predicate(item) ? matching : others).Add(item);
        return (matching, others);
    }
    // --8<-- [end:partition]
}
