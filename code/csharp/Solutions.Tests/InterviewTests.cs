using Solutions.Interview;
using Xunit;

namespace Solutions.Tests;

/// <summary>
/// Appendix D's twenty problems, C# half, against the same cases the
/// Python half is asserted on in code/tests/test_appd.py. Two solutions
/// that agree with their own tests and not with each other would make the
/// appendix's side-by-side claim false.
/// </summary>
public class InterviewTests
{
    [Fact]
    public void D01TwoSum()
    {
        Assert.Equal((0, 1), Problems.TwoSum([2, 7, 11, 15], 9));
        Assert.Equal((0, 1), Problems.TwoSum([3, 3], 6));
        Assert.Null(Problems.TwoSum([1, 2], 99));
        Assert.Null(Problems.TwoSum([], 0));
    }

    [Fact]
    public void D02GroupAnagrams()
    {
        var got = Problems.GroupAnagrams(
            ["eat", "tea", "tan", "ate", "nat", "bat"]);
        Assert.Equal(
            [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]], got);
        Assert.Empty(Problems.GroupAnagrams([]));
    }

    [Fact]
    public void D03FirstUnique()
    {
        Assert.Equal('w', Problems.FirstUnique("swiss"));
        Assert.Null(Problems.FirstUnique("aabb"));
        Assert.Null(Problems.FirstUnique(""));
    }

    [Fact]
    public void D04MergeIntervals()
    {
        Assert.Equal(
            [(1, 6), (8, 10), (15, 18)],
            Problems.MergeIntervals([(1, 3), (2, 6), (8, 10), (15, 18)]));
        Assert.Equal([(1, 5)], Problems.MergeIntervals([(1, 4), (4, 5)]));
        Assert.Equal([(1, 9)], Problems.MergeIntervals([(1, 9), (3, 4)]));
        Assert.Empty(Problems.MergeIntervals([]));
    }

    [Fact]
    public void D05Balanced()
    {
        Assert.True(Problems.Balanced("{[()]}"));
        Assert.True(Problems.Balanced(""));
        Assert.False(Problems.Balanced("(]"));
        Assert.False(Problems.Balanced("("));
        Assert.False(Problems.Balanced(")"));
    }

    [Fact]
    public void D06Dedupe()
    {
        Assert.Equal([3, 1, 2], Problems.Dedupe([3, 1, 3, 2, 1]));
        Assert.Empty(Problems.Dedupe(Array.Empty<int>()));
    }

    [Fact]
    public void D07Chunk()
    {
        Assert.Equal(
            [[1, 2], [3, 4], [5]], Problems.Chunk([1, 2, 3, 4, 5], 2));
        Assert.Empty(Problems.Chunk(Array.Empty<int>(), 3));
        Assert.Throws<ArgumentOutOfRangeException>(
            () => Problems.Chunk([1], 0));
    }

    [Fact]
    public void D08Transpose()
    {
        Assert.Equal(
            [[1, 4], [2, 5], [3, 6]],
            Problems.Transpose([[1, 2, 3], [4, 5, 6]]));
        // The ragged guard, written by hand here and given by
        // zip(strict=True) on the Python side.
        Assert.Throws<ArgumentException>(
            () => Problems.Transpose([[1, 2], [3]]));
    }

    [Fact]
    public void D09Flatten()
    {
        object[] nested = [1, new object[] { 2, new object[] { 3, 4 } }, 5];
        Assert.Equal([1, 2, 3, 4, 5], Problems.Flatten(nested));
        Assert.Empty(Problems.Flatten([]));
    }

    [Fact]
    public void D10TopWords()
    {
        Assert.Equal(
            [("the", 3), ("cat", 2)],
            Problems.TopWords("The cat, the dog; the CAT.", 2));
    }

    [Fact]
    public void D11BinarySearch()
    {
        Assert.Equal(2, Problems.IndexOf([1, 3, 5, 7], 5));
        Assert.Equal(0, Problems.IndexOf([1, 3, 5, 7], 1));
        Assert.Equal(-1, Problems.IndexOf([1, 3, 5, 7], 4));
        Assert.Equal(-1, Problems.IndexOf([], 1));
    }

    [Fact]
    public void D12RunningTotal()
    {
        Assert.Equal([1, 3, 6, 10], Problems.RunningTotal([1, 2, 3, 4]));
        Assert.Empty(Problems.RunningTotal([]));
    }

    [Fact]
    public void D13Rotate()
    {
        Assert.Equal([3, 4, 5, 1, 2], Problems.Rotate([1, 2, 3, 4, 5], 2));
        Assert.Equal([3, 4, 5, 1, 2], Problems.Rotate([1, 2, 3, 4, 5], 7));
        // The correction C#'s % needs and Python's does not.
        Assert.Equal([5, 1, 2, 3, 4], Problems.Rotate([1, 2, 3, 4, 5], -1));
        Assert.Empty(Problems.Rotate(Array.Empty<int>(), 3));
    }

    [Fact]
    public void D14LongestCommonPrefix()
    {
        Assert.Equal(
            "fl", Problems.LongestCommonPrefix(["flower", "flow", "flight"]));
        Assert.Equal("", Problems.LongestCommonPrefix(["dog", "car"]));
        Assert.Equal("same", Problems.LongestCommonPrefix(["same", "same"]));
        Assert.Equal("", Problems.LongestCommonPrefix([]));
    }

    [Fact]
    public void D15IsPalindrome()
    {
        Assert.True(Problems.IsPalindrome("A man, a plan, a canal: Panama"));
        Assert.True(Problems.IsPalindrome(""));
        Assert.False(Problems.IsPalindrome("hello"));
    }

    [Fact]
    public void D16DeepGet()
    {
        IReadOnlyDictionary<string, object?> config =
            new Dictionary<string, object?>
            {
                ["db"] = new Dictionary<string, object?>
                {
                    ["primary"] = new Dictionary<string, object?>
                    {
                        ["port"] = 5432,
                    },
                },
            };
        Assert.Equal(5432, Problems.DeepGet(config, "db.primary.port"));
        Assert.Equal(0, Problems.DeepGet(config, "db.replica.port", 0));
        Assert.Equal(
            "x", Problems.DeepGet(config, "db.primary.port.deeper", "x"));
    }

    [Fact]
    public void D17DedupeBy()
    {
        (int Id, string V)[] rows = [(1, "a"), (1, "b"), (2, "c")];
        Assert.Equal(
            [(1, "a"), (2, "c")], Problems.DedupeBy(rows, r => r.Id));
    }

    [Fact]
    public void D18LatestPerKey()
    {
        (string User, int At)[] rows =
            [("ada", 1), ("ada", 5), ("bob", 2)];
        Assert.Equal(
            [("ada", 5), ("bob", 2)],
            Problems.LatestPerKey(rows, r => r.User, r => r.At));
    }

    [Fact]
    public void D19PairwiseDiff()
    {
        Assert.Equal([3, -1, 8], Problems.PairwiseDiff([10, 13, 12, 20]));
        Assert.Empty(Problems.PairwiseDiff([7]));
        Assert.Empty(Problems.PairwiseDiff([]));
    }

    [Fact]
    public void D20Partition()
    {
        var (matching, others) =
            Problems.Partition([1, 2, 3, 4, 5], n => n % 2 == 0);
        Assert.Equal([2, 4], matching);
        Assert.Equal([1, 3, 5], others);
    }
}
