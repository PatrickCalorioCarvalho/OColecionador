import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'OColecionadorBackEnd',
      items: [
        'ocolecionadorbackend',
        'ocolecionadorbackend-advanced',
      ],
    },
    {
      type: 'category',
      label: 'OColecionadorAugmentations',
      items: [
        'ocolecionadoraugmentations',
        'ocolecionadoraugmentations-advanced',
      ],
    },
    {
      type: 'category',
      label: 'OColecionadorClassifier',
      items: [
        'ocolecionadorclassifier',
        'ocolecionadorclassifier-advanced',
      ],
    },
        {
      type: 'category',
      label: 'OColecionadorTraining',
      items: [
        'ocolecionadortraining',
        'ocolecionadortraining-advanced',
      ],
    },
        {
      type: 'category',
      label: 'OColecionadorFrontEnd',
      items: [
        'ocolecionadorfrontend',
        'ocolecionadorfrontend-advanced',
      ],
    },
        {
      type: 'category',
      label: 'OColecionadorMobile',
      items: [
        'ocolecionadormobile',
        'ocolecionadormobile-advanced',
      ],
    },
    {
      type: 'category',
      label: 'Arquitetura, CI/CD e Infraestrutura',
      items: [
        'arquitetura-cicd-infraestrutura',
        'arquitetura-cicd-infraestrutura-advanced',
      ],
    }
  ],
};

export default sidebars;