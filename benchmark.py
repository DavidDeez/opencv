import time
import cv2
import numpy as np
import os
import platform
from vision import annotate_ui_elements

def generate_dummy_image(path):
    """Generates a synthetic 1080p UI screenshot if one doesn't exist."""
    print("Generating synthetic 1080p UI for benchmark...")
    img = np.ones((1080, 1920, 3), dtype=np.uint8) * 240
    # Draw some fake UI buttons
    for _ in range(30):
        pt1 = (np.random.randint(0, 1800), np.random.randint(0, 1000))
        pt2 = (pt1[0] + np.random.randint(80, 300), pt1[1] + np.random.randint(30, 80))
        cv2.rectangle(img, pt1, pt2, (200, 200, 200), -1)
    cv2.imwrite(path, img)

def run_benchmark(iterations=150):
    print("\n=====================================================")
    print("  OpenCV 5 COOL Benchmark (Target: AWS Graviton)")
    print("=====================================================")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_img = os.path.join(current_dir, "benchmark_test.png")
    out_img = os.path.join(current_dir, "benchmark_out.png")
    
    if not os.path.exists(test_img):
        generate_dummy_image(test_img)
        
    print(f"System Architecture: {platform.machine()}")
    print(f"Running {iterations} iterations of the Vision Perception pipeline...")
    
    # Warmup loop to populate caches
    for _ in range(5):
        annotate_ui_elements(test_img, out_img)
        
    start_time = time.time()
    
    # Actual Benchmark
    for _ in range(iterations):
        annotate_ui_elements(test_img, out_img)
        
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_latency_ms = (total_time / iterations) * 1000
    throughput_fps = iterations / total_time
    
    print("\n=== BENCHMARK RESULTS ===")
    print(f"Total Time:      {total_time:.4f} seconds")
    print(f"Average Latency: {avg_latency_ms:.2f} ms per frame")
    print(f"Throughput:      {throughput_fps:.2f} frames per second (FPS)")
    
    print("\n--- DEVPOST SUBMISSION INSTRUCTIONS ---")
    print("To qualify for the $1,000 COOL Prize, run this script twice:")
    print("1. On a standard x86 instance (e.g. t3.medium)")
    print("2. On an AWS Graviton instance (e.g. t4g.medium) with COOL installed")
    print("Compare the Throughput (FPS) difference in your final presentation.")
    print("=====================================================\n")

if __name__ == "__main__":
    run_benchmark(200)
