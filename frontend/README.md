# next-template

A Next.js 13 template for building apps with Radix UI and Tailwind CSS.

## Usage

```bash
npx create-next-app -e https://github.com/shadcn/next-template
```

## Features

- Next.js 13 App Directory
- [Shadcn UI](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/docs/installation)
- Icons from [Lucide](https://lucide.dev) and [Heroicons](https://heroicons.com/)
- Dark mode with `next-themes`
- Tailwind CSS class sorting, merging and linting.
- [DeckGL](https://deck.gl/docs) and [MapLibre](https://maplibre.org/maplibre-gl-js/docs/) with [`react-map-gl`](https://visgl.github.io/react-map-gl/docs) for map interactivity and visualization
- [Zustand](https://docs.pmnd.rs/zustand/getting-started/introduction) and [Jotai](https://jotai.org/docs/introduction) for state management
- [Framer Motion](https://www.framer.com/motion/) for custom animations

## Getting started

- First unzip all archives in `./public/data/geometries` folder

  ```shell
  gunzip *.gz
  ```

- Then as usual, install dependencies and start dev server

```shell
npm install
npm run dev
```

## Nota Bene

For now, GeoJSON files are served via a public endpoint provided by NextJS. Soon, this will be moved to NextJS server routes to enhance caching.
Some geographic features will be displayed as DeckGL GeoJsonLayer in this first version but to enhance vizualization performance these static layers (e.g harbour locations, marine protected areas... and even historic vessels tracks) should be served as vector tiles for example with [PMTiles](https://docs.protomaps.com/pmtiles/) files stored in the cloud (a MinIO instance for example). PMTiles suuport in DeckGL [should be evaluated](https://github.com/visgl/deck.gl/discussions/7861), MVT/MBTiles [are already supported](https://deck.gl/docs/api-reference/geo-layers/mvt-layer).

## Clever Cloud

Deploy with Clever Cloud:

```bash
cd frontend
clever deploy -f
```

## License

Licensed under the [MIT license](https://github.com/shadcn/ui/blob/main/LICENSE.md).
