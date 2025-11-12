import type { Config } from '@docusaurus/types';
import { themes as prismThemes } from 'prism-react-renderer';

const config: Config = {
  title: 'O Colecionador',
  tagline: 'Classificação de imagens com IA',
  url: 'https://patrickcaloriocarvalho.github.io',
  baseUrl: '/OColecionador/',
  favicon: 'img/favicon.ico',
  organizationName: 'PatrickCalorioCarvalho',
  projectName: 'OColecionador',
  deploymentBranch: 'gh-pages',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.ts'),
          editUrl:
            'https://github.com/PatrickCalorioCarvalho/OColecionador/edit/main/Documentation/docs/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'O Colecionador',
      logo: {
        alt: 'Logo O Colecionador',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Documentação',
        },
        {
          href: 'https://louse-model-lioness.ngrok-free.app/login',
          label: 'Frontend',
          position: 'right',
        },
        {
          href: 'https://hub.docker.com/u/patrickcaloriocarvalho',
          label: 'Docker Hub',
          position: 'right',
        },
        {
          href: 'https://github.com/PatrickCalorioCarvalho/OColecionador',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Projeto',
          items: [
            {
              label: 'Frontend',
              href: 'https://louse-model-lioness.ngrok-free.app/login',
            },
            {
              label: 'Docker Hub',
              href: 'https://hub.docker.com/u/patrickcaloriocarvalho',
            },
          ],
        },
        {
          title: 'Comunidade',
          items: [
            {
              label: 'GitHub Issues',
              href: 'https://github.com/PatrickCalorioCarvalho/OColecionador/issues',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} O Colecionador.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },
};

export default config;
