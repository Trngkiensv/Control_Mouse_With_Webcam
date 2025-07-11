import multiprocessing
import time


def main(queue):
    last_receive_time = None
    while True:
        try:
            # Lấy dữ liệu từ queue
            landmark_list, hand_sign_id = queue.get_nowait()
            current_time = time.time()

            # Tính độ trễ
            if last_receive_time is not None:
                latency = (current_time - last_receive_time) * 1000  # Chuyển sang ms
                print(f"Latency: {latency:.2f} ms")
            last_receive_time = current_time

            # Xử lý dữ liệu
            if not landmark_list or hand_sign_id is None:
                print("No hand detected: signID=None, kp0=None")
            else:
                if len(landmark_list) != 21 or not all(len(coord) == 2 for coord in landmark_list):
                    print("Invalid landmark data: signID=None, kp0=None")
                else:
                    kp0 = landmark_list[0]  # Keypoint 0 (wrist)
                    print(f"Received: signID={hand_sign_id}, kp0={kp0}")
        except multiprocessing.queues.Empty:
            pass  # No new data, skip
        except (ValueError, TypeError) as e:
            print(f"Error processing queue data: {e}")


if __name__ == "__main__":
    queue = multiprocessing.Queue(maxsize=200)
    main(queue)