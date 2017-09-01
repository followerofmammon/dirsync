import replicas_from_args
import interactive_diff_sync
import search_supplement_replicas

################# searchreplicas

def sync_from_src_to_dst(src, dst):
    diffsync = interactive_diff_sync.InteractiveDiffSync(src, dst)
    diffsync.sync()

def sync(replica_a, replica_b):
    sync_from_src_to_dst(src=replica_a, dst=replica_b)
    sync_from_src_to_dst(src=replica_b, dst=replica_a)


################# main
def main():
    replica_a_path, replica_b_path = replicas_from_args.get()
    replica_a_path, replica_b_path = search_supplement_replicas.search(replica_a_path,
                                                                       replica_b_path)
    sync(replica_a_path, replica_b_path)

if __name__ == "__main__":
    main()
