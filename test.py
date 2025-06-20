
# Mở file ở chế độ ghi ('w') và ghi một giá trị
with open('landmarks.txt', 'w') as file:# Giá trị muốn ghi
    for i in range(10):
        file.write(f"{i}:{landmark_list[i]}\n")