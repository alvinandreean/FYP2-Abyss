export interface AttackResult {
    epsilon_used: number;
    orig_class: string;
    orig_conf: number;
    adv_class: string;
    adv_conf: number;
    original_image: string;
    perturbation_image: string;
    adversarial_image: string;
    model_used?: string; 
  }