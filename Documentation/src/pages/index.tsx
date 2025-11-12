import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Head from '@docusaurus/Head';

export default function Home() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout>
      <Head>
        <title>{siteConfig.title}</title>
        <meta name="description" content={siteConfig.tagline} />
      </Head>
      <main style={{ textAlign: 'center', padding: '4rem' }}>

        <div style={{ marginTop: '3rem' }}>
          <img
            src="/img/icon.png"
            alt="Ícone O Colecionador"
            style={{ width: '300px' }}
          />
        </div>

        <h1>O Colecionador</h1>
        <p>
          Projeto de classificação de imagens com integração de Backend, Frontend, Mobile e IA.
        </p>

        {/* Botões principais */}
        <div style={{ marginTop: '2rem' }}>
          <Link
            className="button button--primary button--lg"
            to="/docs/intro"
          >
            📖 Documentação
          </Link>
          <Link
            className="button button--secondary button--lg"
            href="https://louse-model-lioness.ngrok-free.app/login"
            style={{ marginLeft: '1rem' }}
          >
            🌐 Frontend
          </Link>
          <Link
            className="button button--secondary button--lg"
            href="https://hub.docker.com/u/patrickcaloriocarvalho"
            style={{ marginLeft: '1rem' }}
          >
            🐳 Docker Hub
          </Link>
          <Link
            className="button button--secondary button--lg"
            href="https://github.com/PatrickCalorioCarvalho/OColecionador"
            style={{ marginLeft: '1rem' }}
          >
            💻 GitHub
          </Link>
        </div>
      </main>
    </Layout>
  );
}
