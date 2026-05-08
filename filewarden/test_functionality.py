import sys
import time
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from core.rules import Rule, Sentinel
from core.watcher import FileWatcherThread

def main():
    app = QApplication(sys.argv)
    
    # Setup test directories
    test_dir = Path("./test_env")
    watch_dir = test_dir / "watch"
    dest_dir = test_dir / "dest"
    outside_dir = test_dir / "outside"
    
    for d in [watch_dir, dest_dir, outside_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    # Rules
    rule1 = Rule("txt, md", dest_dir, "move")
    sentinel = Sentinel(watch_path=watch_dir, rules=[rule1], active=True)
    
    # Start thread
    thread = FileWatcherThread([sentinel])
    
    def on_moved(msg):
        print(f"[TEST SUCCESS] {msg}")
        
    def on_err(msg):
        print(f"[TEST ERROR] {msg}")
        
    thread.file_moved.connect(on_moved)
    thread.error_occurred.connect(on_err)
    thread.start()
    
    # Wait for observer to start
    time.sleep(1)
    
    # Test 1: create file inside (simulating download or external program creation)
    print("Testing create event...")
    test_file_1 = watch_dir / "test1.txt"
    test_file_1.write_text("hello")
    time.sleep(2) # wait for event
    
    # Test 2: move file from outside into watch dir (simulating drag and drop)
    print("Testing move event...")
    test_file_2_out = outside_dir / "test2.md"
    test_file_2_out.write_text("world")
    
    # move
    shutil.move(str(test_file_2_out), str(watch_dir / "test2.md"))
    time.sleep(2)
    
    thread.stop()
    # No need to app.exec() since we're just waiting with time.sleep
    # and QThread signals work if we give it time or process events,
    # but wait, QThread signals need event loop.
    # Let's process events.
    app.processEvents()
    
    # cleanup
    try:
        shutil.rmtree(test_dir)
    except:
        pass
    print("Tests completed.")

if __name__ == "__main__":
    main()
