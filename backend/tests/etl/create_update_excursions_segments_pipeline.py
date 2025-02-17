from bloom.container import UseCases
if __name__ == "__main__":
    pipeline = UseCases.create_update_excursions_segments_pipeline()
    pipeline.run()