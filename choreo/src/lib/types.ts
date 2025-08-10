
export type ArticleMetadata = {
  title: string;
  author: string | null;
  published_date: string | null;
  favicon: string | null;
  meta_image: string | null;
};

export type YoutubeVideoMetadata = {
  title: string;
  channel: string | null;
  published_date: string | null;
  thumbnail_url: string | null;
};
