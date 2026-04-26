/**
 * E2E Tests for Plan Mode Functionality
 */


describe('Plan Mode E2E Tests', () => {
  beforeEach(() => {
    // Set up test environment
    localStorage.clear();
    localStorage.setItem('auth_token', 'test_token');
    cy.visit('/');
  });

  describe('Plan Mode Navigation', () => {
    it('should display plan mode panel', () => {
      cy.get('[data-testid="sidebar-plan-mode"]').should('be.visible');
    });

    it('should toggle plan mode visibility', () => {
      cy.get('[data-testid="toggle-plan-mode"]').click();
      cy.get('[data-testid="plan-panel"]').should('be.visible');

      cy.get('[data-testid="toggle-plan-mode"]').click();
      cy.get('[data-testid="plan-panel"]').should('not.be.visible');
    });

    it('should navigate to plan mode panel', () => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.url().should('include', '/plan');
      cy.get('[data-testid="plan-container"]').should('exist');
    });
  });

  describe('Plan Creation', () => {
    it('should create new plan', () => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').click();

      cy.get('[data-testid="plan-name-input"]').type('Test Plan');
      cy.get('[data-testid="plan-description-input"]').type('Test plan description');
      cy.get('[data-testid="save-plan-btn"]').click();

      cy.get('[data-testid="plan-list"]').should('contain', 'Test Plan');
    });

    it('should validate plan name is required', () => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="save-plan-btn"]').click();

      cy.get('[data-testid="plan-name-error"]').should('contain', 'Plan name is required');
    });

    it('should cancel plan creation', () => {
      cy.get('[data-testid="nav-plan"]').click();
      const initialCount = cy.get('[data-testid="plan-item"]').length;

      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="plan-name-input"]').type('Cancelled Plan');
      cy.get('[data-testid="cancel-plan-btn"]').click();

      cy.get('[data-testid="plan-item"]').should('have.length', initialCount);
    });
  });

  describe('Plan Editing', () => {
    beforeEach(() => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="plan-name-input"]').type('Editable Plan');
      cy.get('[data-testid="save-plan-btn"]').click();
    });

    it('should edit existing plan', () => {
      cy.get('[data-testid="plan-item"]').first().within(() => {
        cy.get('[data-testid="edit-plan-btn"]').click();
      });

      cy.get('[data-testid="plan-name-input"]').clear().type('Updated Plan');
      cy.get('[data-testid="save-plan-btn"]').click();

      cy.get('[data-testid="plan-list"]').should('contain', 'Updated Plan');
    });

    it('should delete plan', () => {
      cy.get('[data-testid="plan-item"]').first().within(() => {
        cy.get('[data-testid="delete-plan-btn"]').click();
      });

      cy.get('[data-testid="confirm-delete"]').click();
      cy.get('[data-testid="plan-list"]').should('not.contain', 'Editable Plan');
    });
  });

  describe('Plan Steps', () => {
    beforeEach(() => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="plan-name-input"]').type('Multi-step Plan');
      cy.get('[data-testid="save-plan-btn"]').click();
      cy.get('[data-testid="plan-item"]').first().click();
    });

    it('should add plan step', () => {
      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('ls -la');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="plan-step"]').should('have.length', 1);
    });

    it('should execute plan step', () => {
      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('echo test');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="step-result"]').should('contain', 'test');
      cy.get('[data-testid="step-status"]').should('contain', 'success');
    });

    it('should display step error on failure', () => {
      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('invalid_command_xyz');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="step-error"]').should('be.visible');
      cy.get('[data-testid="step-status"]').should('contain', 'error');
    });

    it('should delete plan step', () => {
      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('ls');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="plan-step"]').first().within(() => {
        cy.get('[data-testid="delete-step-btn"]').click();
      });

      cy.get('[data-testid="plan-step"]').should('have.length', 0);
    });
  });

  describe('Plan Execution', () => {
    beforeEach(() => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="plan-name-input"]').type('Execution Plan');
      cy.get('[data-testid="save-plan-btn"]').click();
      cy.get('[data-testid="plan-item"]').first().click();
    });

    it('should execute full plan', () => {
      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('echo step1');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('echo step2');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="execute-all-btn"]').click();

      cy.get('[data-testid="plan-result"]').should('contain', 'step1');
      cy.get('[data-testid="plan-result"]').should('contain', 'step2');
    });

    it('should show execution progress', () => {
      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('sleep 1 && echo done');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="execution-progress"]').should('be.visible');
      cy.get('[data-testid="execution-progress"]').should('contain', '0%');
    });
  });

  describe('Plan State Persistence', () => {
    it('should persist plan to localStorage', () => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="plan-name-input"]').type('Persistent Plan');
      cy.get('[data-testid="save-plan-btn"]').click();

      cy.reload();

      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="plan-list"]').should('contain', 'Persistent Plan');
    });

    it('should save plan execution history', () => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="plan-name-input"]').type('History Plan');
      cy.get('[data-testid="save-plan-btn"]').click();
      cy.get('[data-testid="plan-item"]').first().click();

      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('echo test');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="plan-history"]').should('be.visible');
      cy.get('[data-testid="history-item"]').should('have.length.greaterThan', 0);
    });
  });

  describe('Plan Keyboard Shortcuts', () => {
    beforeEach(() => {
      cy.get('[data-testid="nav-plan"]').click();
    });

    it('should create new plan with Ctrl+N', () => {
      cy.get('body').type('{ctrl}n');
      cy.get('[data-testid="plan-form"]').should('be.visible');
    });

    it('should execute plan with Ctrl+Enter', () => {
      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="plan-name-input"]').type('Shortcut Plan');
      cy.get('[data-testid="save-plan-btn"]').click();
      cy.get('[data-testid="plan-item"]').first().click();

      cy.get('body').type('{ctrl}{enter}');

      cy.get('[data-testid="plan-result"]').should('be.visible');
    });
  });

  describe('Plan Accessibility', () => {
    it('should have proper ARIA labels', () => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').should('have.attr', 'aria-label');
      cy.get('[data-testid="add-step-btn"]').should('have.attr', 'aria-label');
    });

    it('should be keyboard navigable', () => {
      cy.get('[data-testid="nav-plan"]').focus().type('{enter}');
      cy.url().should('include', '/plan');
    });

    it('should have proper focus management', () => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').focus();
      cy.focused().should('have.attr', 'data-testid', 'create-plan-btn');
    });
  });

  describe('Plan Error Handling', () => {
    it('should handle network errors gracefully', () => {
      cy.intercept('/api/plans', { statusCode: 500 });
      cy.get('[data-testid="nav-plan"]').click();

      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="retry-btn"]').should('be.visible');
    });

    it('should handle invalid commands', () => {
      cy.get('[data-testid="nav-plan"]').click();
      cy.get('[data-testid="create-plan-btn"]').click();
      cy.get('[data-testid="plan-name-input"]').type('Invalid Plan');
      cy.get('[data-testid="save-plan-btn"]').click();
      cy.get('[data-testid="plan-item"]').first().click();

      cy.get('[data-testid="add-step-btn"]').click();
      cy.get('[data-testid="step-command-input"]').type('&&& invalid');
      cy.get('[data-testid="execute-step-btn"]').click();

      cy.get('[data-testid="validation-error"]').should('be.visible');
    });
  });
});
