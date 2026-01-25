def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# 测试代码
arr = [3, 6, 8, 10, 1, 2, 1]
print("原始数组:", arr)
sorted_arr = quick_sort(arr)
print("排序后数组:", sorted_arr)

# 更多测试
arr2 = [64, 34, 25, 12, 22, 11, 90]
print("\n测试2 - 原始数组:", arr2)
print("排序后数组:", quick_sort(arr2))

arr3 = [5, 2, 8, 1, 9, 3]
print("\n测试3 - 原始数组:", arr3)
print("排序后数组:", quick_sort(arr3))