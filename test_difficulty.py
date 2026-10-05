import sys
sys.path.insert(0, '..')
from vaylatilasto_fetcher import calculate_difficulty_from_avg

def test_avg_par_b():
    avg=[4.45,3.77,3.45,3.42,3.55,4.18,3.79,3.33,4.53,4.20,6.15,4.23]
    par=[4,3,3,3,3,3,3,3,4,3,5,4]
    result=calculate_difficulty_from_avg(avg, par)
    expected=[8,5,9,10,6,2,4,11,7,1,3,12]
    assert result==expected, f"B logiikka väärin {result} != {expected}"
    assert set(result)==set(range(1,13))
    print("test_avg_par_b OK")

def test_avg_abs_fallback():
    avg=[4.45,3.77,3.45,3.42,3.55,4.18,3.79,3.33,4.53,4.20,6.15,4.23]
    result=calculate_difficulty_from_avg(avg, None)
    expected=[8,5,9,10,6,2,4,11,7,1,3,12]
    assert result==expected
    print("test_avg_abs OK")

def test_colors():
    from vaylatilasto_fetcher import calculate_dynamic_colors
    avg=[4.45,3.77,3.45,3.42,3.55,4.18,3.79,3.33,4.53,4.20,6.15,4.23]
    par=[4,3,3,3,3,3,3,3,4,3,5,4]
    diff=[8,5,9,10,6,2,4,11,7,1,3,12]
    avg_c, diff_c = calculate_dynamic_colors(avg, par, diff)
    assert avg_c[8]=="green" # pienin avg vihreä
    assert avg_c[11]=="red" # suurin avg punainen
    assert diff_c[10]=="red" # diff 1 punainen
    assert diff_c[12]=="green" # diff 12 vihreä
    print("test_colors OK")

if __name__=="__main__":
    test_avg_par_b()
    test_avg_abs_fallback()
    test_colors()
    print("Kaikki testit OK - V15 B")
